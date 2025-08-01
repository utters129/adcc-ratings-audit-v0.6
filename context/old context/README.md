==============================================================================
FILE: README.md
PROJECT: ADCC Competitive Analytics Platform
PURPOSE:
This file serves as the main entry point and high-level documentation for
the entire project. It provides essential context for developers and AI
assistants (like Cursor) to understand the project's goals, architecture,
and key features.
==============================================================================
ADCC Competitive Analytics Platform
1. Project Overview
Executive Summary: ADCC Competitive Analytics Platform

Introduction

The ADCC Competitive Analytics Platform is a state-of-the-art system designed to bring data-driven intelligence to the forefront of our competitive operations. This platform automates the collection and analysis of athlete performance data, providing a single source of truth to ensure fairness, transparency, and efficiency. Its primary purpose is to equip our leadership with the objective tools needed to make critical decisions regarding Youth Worlds invitations, adult trials seeding, and the integrity of our event registrations.

Key Features & Benefits for Decision-Makers

This platform moves us beyond manual spreadsheets and subjective analysis by providing a powerful, user-friendly web application with the following core features:

Advanced Athlete Rating System: At the heart of the platform is a sophisticated rating system, similar to the ELO system used in chess but more advanced. It continuously updates an athlete's "power ranking" after every match. This rating is more insightful than a simple win-loss record because it intelligently considers:

Strength of Competition: Beating a highly-rated opponent results in a larger rating increase than beating a lower-rated one.

Decisiveness of Victory: A win by submission is weighted more heavily than a win by decision, rewarding more dominant performances.

Periods of Inactivity: The system smartly accounts for athletes who haven't competed in a while, ensuring their rating accurately reflects their current competitive form.

One-Click Registration Auditing: To eliminate "sandbagging" and ensure competitive integrity, the platform features a powerful auditing tool. You can simply provide the registration link for an upcoming event, and the system will automatically cross-reference every athlete against their historical medal count and skill level. It will instantly generate a clear, actionable list of any competitors registered in a division below their demonstrated skill level.

Dynamic Leaderboards and Athlete Insights: The platform provides a comprehensive and easy-to-navigate web interface where you can:

Query Any Athlete: Instantly pull up a detailed profile for any competitor, including their current rating, a graph of their historical performance, a full breakdown of medals won, and a complete match history.

Generate Custom Rankings: Create and filter leaderboards based on any combination of criteria, such as age class, weight, gender, skill division, and rating. This allows for precise, data-backed analysis when seeding brackets or comparing athletes for invitations.

2. Core Architectural Decisions
This section summarizes the key technical decisions that define how the system works. This is critical context for any AI-driven development.

Application Architecture: The system is a Web-Based Application. The backend is built with Python and the FastAPI framework, serving data to a dynamic frontend. This was chosen for its high performance, accessibility, and ease of maintenance.

Data Source: The primary source of data is Smoothcomp.com. The system uses a Selenium-based web scraper to automate the download of registration and match data files. The entire system is ID-based, using the unique IDs provided in the Smoothcomp data as the single source of truth for athletes and events.

Rating System: The platform uses a customized Glicko-2 rating algorithm.

Weighted Wins: The standard algorithm has been modified to account for the decisiveness of victories (e.g., a submission is worth more than a decision).

Hybrid Rating Periods: To provide timely updates while accurately modeling inactivity, the system uses a hybrid model. Ratings are updated provisionally after each event for immediate feedback, and are finalized at the end of a one-month rating period to correctly apply the time-based Rating Deviation (RD) increase.

State Management & Recovery: The system is designed for robustness with a powerful state management system.

Save States: A complete snapshot of the athlete database is saved after each monthly rating period is finalized.

Multi-Level Resets: The system includes administrative tools for multi-level resets, from a full "hard reset" to a "soft reset" of only the analytics, allowing for fast recalculations without re-processing all raw data.

Chronological Rollbacks: The system can be surgically reverted to any previous monthly state to correct historical errors.

3. How to Use This Repository with Cursor
This project is designed to be built with an AI assistant like Cursor. The source code is provided as detailed, commented-out "blueprint" files.

Provide Context: Start your chat session by telling the AI to read this README.md file and the .cursorrules file to understand the project's goals and coding standards.

Generate Code File-by-File: Open a commented file (e.g., src/core/models.py).

Instruct the AI: Use the chat or inline editor (Ctrl+K) to ask the AI to implement the code based on the detailed comments within that file.

Review and Commit: Review the generated code, and once you are satisfied, use Git to commit the changes with a clear message.

Follow the Development Order: Implement the files in the logical order laid out in the development plan to ensure dependencies are met.