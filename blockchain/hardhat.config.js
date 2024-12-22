require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config(); // Ensure this is included at the top

module.exports = {
  solidity: "0.8.18",
  networks: {
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL || "", // Fallback to empty string
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [], // Fallback to empty array
    },
  },
};

