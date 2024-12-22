from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from web3 import Web3
import json
from datetime import datetime
import os

# Initialize Flask App
app = Flask(_)

# Configure database (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voting_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Connect to Ethereum-compatible testnet (e.g., Sepolia)
w3 = Web3(Web3.HTTPProvider('https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID'))

# Load contract ABI and address
contract_abi = json.loads('[...]')  # Replace with actual ABI from your compiled contract
contract_address = '0xYourContractAddress'

# Initialize contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Models (assuming you already have them set up as in the previous response)
from models import User, Poll, Vote


# Route to create a poll (admin only)
@app.route('/create_poll', methods=['POST'])
def create_poll():
    data = request.get_json()
    title = data.get('title')
    options = data.get('options')
    deadline = data.get('deadline')

    # Validate data
    if not title or not options or not deadline:
        return jsonify({"message": "Missing data"}), 400

    # Create Poll in the database
    poll = Poll(title=title, options=options, start_date=datetime.utcnow(), end_date=deadline, creator_id=1)
    db.session.add(poll)
    db.session.commit()

    # Call smart contract to create poll on the blockchain
    tx_hash = create_poll_on_blockchain(title, options, deadline)

    return jsonify({"message": "Poll created successfully", "transaction_hash": tx_hash.hex()}), 201


# Function to interact with blockchain and create poll
def create_poll_on_blockchain(title, options, deadline):
    tx = contract.functions.createPoll(title, options, deadline).buildTransaction({
        'from': '0xYourWalletAddress',
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount('0xYourWalletAddress'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='YourPrivateKey')
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash


# Route to vote on a poll (registered user)
@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    user_id = data.get('user_id')
    poll_id = data.get('poll_id')
    option = data.get('option')

    # Validate data
    if not user_id or not poll_id or not option:
        return jsonify({"message": "Missing data"}), 400

    # Record vote in the database
    vote = Vote(user_id=user_id, poll_id=poll_id, option=option, transaction_hash='some_hash')
    db.session.add(vote)
    db.session.commit()

    # Call smart contract to record vote on blockchain
    tx_hash = cast_vote_on_blockchain(poll_id, option)

    return jsonify({"message": "Vote cast successfully", "transaction_hash": tx_hash.hex()}), 200


# Function to interact with blockchain and cast vote
def cast_vote_on_blockchain(poll_id, option):
    tx = contract.functions.vote(poll_id, option).buildTransaction({
        'from': '0xYourWalletAddress',
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei'),
        'nonce': w3.eth.getTransactionCount('0xYourWalletAddress'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key='YourPrivateKey')
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash


# Route to view poll results
@app.route('/view_results/<int:poll_id>', methods=['GET'])
def view_results(poll_id):
    # Query database for poll and votes
    poll = Poll.query.get_or_404(poll_id)
    votes = Vote.query.filter_by(poll_id=poll_id).all()

    # Fetch results from the blockchain
    blockchain_results = contract.functions.getPollResults(poll_id).call()

    results = {poll.options[i]: blockchain_results[i] for i in range(len(poll.options))}
    
    return jsonify({
        "poll_title": poll.title,
        "results": results
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
