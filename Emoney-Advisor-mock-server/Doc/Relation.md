          +--------+
          |  USER  |
          +--------+
           /|     |\
 creates  / |     | \  manages
         /  |     |  \
        v   |     |   v
 +--------+ |     | +-----------+
 | CLIENT | |     | |    FIRM   |
 +--------+ |     | +-----------+
     |      |     |      |
     |      |     |      |
     v      |     |      v
+----------+|     |+------------+
| CONTACT  ||     || WORKSPACE  |
+----------+|     |+------------+
     |      |     |      |
     |      |     |      |
     v      |     |      v
+-----------+     +--------------+
| HOUSEHOLD |     | FINANCIAL    |
|           |<----| PLAN         |
+-----------+     +--------------+
     |                  |
     |                  |
     v                  v
+-------------+    +----------+
|RELATIONSHIP |    |   GOAL   |
+-------------+    +----------+
                        |
                        |
                        v
                   +----------+
                   | SCENARIO |
                   +----------+
                        |
                        |
                        v
                   +----------+
                   | CASHFLOW |
                   +----------+
                        |
                        |
                        v
     +--------+    +----------+    +-------------+
     | ASSET  |<---|  ACCOUNT |<---| RETIREMENT  |
     +--------+    +----------+    | PLAN        |
         |              |          +-------------+
         |              |               |
         v              v               v
  +------------+  +------------+  +----------+
  | ALLOCATION |  | INVESTMENT |  | PENSION  |
  +------------+  +------------+  +----------+
         |              |               |
         |              |               v
         v              v          +---------------+
  +------------+  +------------+   | SOCIAL       |
  | SECURITY   |  | LIABILITY  |   | SECURITY     |
  +------------+  +------------+   +---------------+
                        |                |
                        |                v
                        v           +--------+
                   +--------+       |  RMD   |
                   | INCOME |       +--------+
                   +--------+            |
                        |                |
                        v                v
                   +----------+    +------------+
                   | SPENDING |    | INSURANCE  |
                   +----------+    +------------+
                        |                |
                        |                |
                        v                v
                   +----------+    +----------+
                   |  BUDGET  |    |  POLICY  |
                   +----------+    +----------+
                        |                |
                        |                |
                        v                v
                   +----------+    +----------+
                   | EXPENSE  |    | COVERAGE |
                   +----------+    +----------+
                                        |
                                        |
                                        v
                                   +----------+
                                   | PREMIUM  |
                                   +----------+

                +--------+    +-------------+    +-----------+
                | ESTATE |<-->| TAX PLAN    |<-->| DOCUMENT  |
                +--------+    +-------------+    +-----------+
                    |               |                 |
                    |               |                 |
                    v               v                 v
                +--------+    +-------------+    +-----------+
                |  WILL  |    | TAX BRACKET |    |   VAULT   |
                +--------+    +-------------+    +-----------+
                    |               |                 |
                    |               |                 |
                    v               v                 v
                +--------+    +-------------+    +-----------+
                | TRUST  |    |  DEDUCTION  |    | FILE TYPE |
                +--------+    +-------------+    +-----------+
                    |               |                 |
                    |               |                 |
                    v               v                 v
                +------------+  +----------+    +-----------+
                | BENEFICIARY|  |  CREDIT  |    |ATTACHMENT |
                +------------+  +----------+    +-----------+
Key Relationships:

User Management

USER creates and manages CLIENT records
USER belongs to a FIRM
USER works within WORKSPACE


Client Relationships

CLIENT has multiple CONTACT records
CLIENT belongs to HOUSEHOLD groups
RELATIONSHIP connects CLIENTs to each other


Financial Planning

FINANCIAL PLAN belongs to a CLIENT
FINANCIAL PLAN contains multiple GOALs
SCENARIO models different planning approaches
CASHFLOW projects income and expenses


Account Structure

ACCOUNT belongs to a CLIENT
ACCOUNT contains INVESTMENTs
ACCOUNT may be linked to a RETIREMENT PLAN
ASSET records are associated with CLIENTs and ACCOUNTs


Retirement Planning

RETIREMENT PLAN includes PENSION records
RETIREMENT PLAN includes SOCIAL SECURITY projections
RMD calculations for retirement accounts


Spending Management

INCOME sources feed into SPENDING records
BUDGET establishes spending limits
EXPENSE tracks individual transactions


Insurance Planning

INSURANCE portfolio contains multiple POLICYs
POLICY defines specific COVERAGE details
PREMIUM tracks payments for policies


Estate Planning

ESTATE plan includes WILL and TRUST documents
BENEFICIARY records are linked to estate documents


Tax Planning

TAX PLAN references applicable TAX BRACKET information
TAX PLAN includes DEDUCTION and CREDIT records


Document Management

DOCUMENT stored in VAULT
FILE TYPE categorizes documents
ATTACHMENT links documents to various entities



This diagram shows the comprehensive relationships between the different entities in the financial advisory system, with each domain having its own cluster of related entities while maintaining connections to other domains.