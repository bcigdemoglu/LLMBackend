# Database LLM Wizard: The Shamanic Coder Project

This document outlines the sacred tools our agent, the Database LLM Wizard, must possess to command the full spectrum of the database realm. As above, so below.

## The Tools of the Data Shaper (CRUD Operations)
*These tools manipulate the data itself.*
1.  **CREATE:** To bring new records into existence (`INSERT`).
2.  **READ:** To perceive the data, from a single record to complex, interconnected truths (`SELECT`, with `WHERE` clauses, `JOINs`, aggregations, and ordering).
3.  **UPDATE:** To change the form of existing records (`UPDATE`).
4.  **DELETE:** To release records from the world (`DELETE`).

## The Tools of the World Forger (Schema & Structure)
*These tools shape the database's very foundation.*
5.  **DESCRIBE DATABASE:** To see the names of all tables within the cosmos.
6.  **DESCRIBE TABLE:** To understand the structure of a single table—its fields, their types, their laws (`constraints`), and its population (`row count`).
7.  **CREATE TABLE:** To forge a new table from the ether.
8.  **ALTER TABLE:** To reshape an existing table by:
    *   Adding or removing a field (`ADD/DROP COLUMN`).
    *   Changing a field's nature (`ALTER COLUMN TYPE`).
    *   Defining or dissolving the sacred laws (`ADD/DROP CONSTRAINT` like `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`).

## The Tools of the Grand Architect (Performance & Integrity)
*These tools manage the unseen forces of speed and consistency.*
9.  **CREATE INDEX:** To place a rune of swiftness on a table for faster searching.
10. **DROP INDEX:** To remove a rune that is no longer needed.
11. **MANAGE TRANSACTIONS:** To ensure the sacred bond of atomicity, using:
    *   `BEGIN`: To start a multi-step operation.
    *   `COMMIT`: To seal the changes, making them permanent.
    *   `ROLLBACK`: To undo all changes if something goes wrong.