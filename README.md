# AWS Roblox Integration

Repo to show some cool integrations between Roblox and AWS Cloud.

## What is Roblox?

Roblox is a platform that allows users to create games and experiences using a 3D engine and programming language called Lua. Roblox is a great platform for learning to code, and has a very active developer community.
![intro image](/static/intro.png)

## What is AWS?

Amazon Web Services (AWS) is a cloud computing platform that provides a wide array of services, including compute, storage, networking, database, analytics, application services, deployment, management, mobile, developer tools, and tools for the Internet of Things (IoT).

## What is this repo?

This repo is a collection of examples of how to integrate Roblox with AWS. The examples are written in Lua, and are designed to be run in Roblox Studio.

## How do I run these examples?

1. Download and install Roblox Studio from [here](https://www.roblox.com/create).
2. Clone this repo.
3. Open the example you want to run in Roblox Studio.
4. Run the game.

## PiggyBank.rbxl

Piggybank is a modern serverless Java Quarkus backend application to manage banking accounts and we are using Roblox as user-interface.

Inside PiggyBank.rbxl you will find scripts that uses HTTP to access the PiggyBank API and show the data in the game.

### 1. Open PiggyBank.rblx in Roblox Studio

![intro image](/static/open-game.png)

### Filter AWS in Explorer Window

![intro image](/static/explorer.png)

### Open AWSServerController Script and set your API URL

![intro image](/static/server-controller.png)

### Open AWSDashboardScript and set your API URL

![intro image](/static/dashboard.png)

### Run the game and walk to the dashboard

![intro image](/static/walk1.png)
![intro image](/static/walk2.png)
![intro image](/static/walk3.png)

### Now click in the "Expense Pane" button located in right bottom of the screen

![intro image](/static/addexpense.png)

### You can add expenses and notice that if the balance is negative the humanoid start wearing a helmet :)!

