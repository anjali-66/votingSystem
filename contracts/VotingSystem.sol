// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VotingSystem {
    // Struct to represent a Poll
    struct Poll {
        string title;                   // Title of the poll
        string[] options;              // Options for voting
        uint256 endTime;               // Poll deadline
        address creator;               // Creator of the poll
        mapping(uint256 => uint256) votes; // Votes per option
        mapping(address => bool) hasVoted; // Tracks if an address has voted
        bool exists;                   // To check if the poll exists
    }

    // Mapping to store Polls
    mapping(uint256 => Poll) private polls;
    uint256 private pollCount = 0; // Counter for polls

    // Events
    event PollCreated(uint256 pollId, string title, uint256 endTime, address creator);
    event VoteCasted(uint256 pollId, uint256 optionIndex, address voter);
    event PollResult(uint256 pollId, uint256[] results);

    // Modifier to check if poll exists
    modifier pollExists(uint256 pollId) {
        require(polls[pollId].exists, "Poll does not exist");
        _;
    }

    // Function to create a new poll
    function createPoll(string memory title, string[] memory options, uint256 durationInMinutes) public {
        require(bytes(title).length > 0, "Title cannot be empty");
        require(options.length > 1, "At least two options are required");
        require(durationInMinutes > 0, "Duration must be greater than 0");

        Poll storage newPoll = polls[pollCount];
        newPoll.title = title;
        newPoll.options = options;
        newPoll.endTime = block.timestamp + (durationInMinutes * 1 minutes);
        newPoll.creator = msg.sender;
        newPoll.exists = true;

        emit PollCreated(pollCount, title, newPoll.endTime, msg.sender);

        pollCount++;
    }

    // Function to vote on a poll
    function vote(uint256 pollId, uint256 optionIndex) public pollExists(pollId) {
        Poll storage poll = polls[pollId];

        require(block.timestamp <= poll.endTime, "Poll has ended");
        require(optionIndex < poll.options.length, "Invalid option index");
        require(!poll.hasVoted[msg.sender], "You have already voted");

        poll.votes[optionIndex]++;
        poll.hasVoted[msg.sender] = true;

        emit VoteCasted(pollId, optionIndex, msg.sender);
    }

    // Function to fetch poll results
    function getPollResults(uint256 pollId) public view pollExists(pollId) returns (uint256[] memory results) {
        Poll storage poll = polls[pollId];
        results = new uint256[](poll.options.length);

        for (uint256 i = 0; i < poll.options.length; i++) {
            results[i] = poll.votes[i];
        }

        return results;
    }

    // Function to get poll details
    function getPollDetails(uint256 pollId) public view pollExists(pollId) returns (
        string memory title,
        string[] memory options,
        uint256 endTime,
        address creator
    ) {
        Poll storage poll = polls[pollId];
        return (poll.title, poll.options, poll.endTime, poll.creator);
    }
}
