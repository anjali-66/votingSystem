require("dotenv").config();
const hre = require("hardhat");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);

    const VotingSystem = await hre.ethers.getContractFactory("VotingSystem");
    console.log("Got contract factory for VotingSystem.");

    // Attempt to deploy the contract
    try {
        const votingSystem = await VotingSystem.deploy();
        console.log("Deployment transaction hash:", votingSystem.deployTransaction.hash);

        // Wait for the deployment to complete
        await votingSystem.deployed();
        console.log("VotingSystem contract deployed to:", votingSystem.address);
    } catch (error) {
        console.error("Deployment failed:", error);
    }
}

main().catch((error) => {
    console.error("Error in script:", error);
    process.exitCode = 1;
});

