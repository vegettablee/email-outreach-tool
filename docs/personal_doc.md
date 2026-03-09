# Personal Project Documentation
- The point of this file is mostly to document things I have been trying throughout the course of this project. 

Right now, my goal is to get better at bridging system design into implementation, leveraging AI as much as possible. 


The Design-to-Code Bridge Framework

  Core Philosophy

  The Bridge Problem:
  High-Level Design (you're good here)
           ↓
      [THE GAP] ← where you struggle
           ↓
  Code-Level Design (module structure, interfaces, data flows)
           ↓
      [AI excels here]
           ↓
  Implementation (actual code)

  Goal: Build fluency in the middle layer—translating requirements into code-ready specifications without over-specifying implementation
  details.

  ---
  The Recursive Decomposition Framework

  Phase 1: Requirement → Module Boundary (Your Design Work)

  Input: High-level requirement
  Output: Module names, responsibilities, interfaces

  The Question Set:
  1. What are the verbs? (actions become functions/methods)
  2. What are the nouns? (entities become classes/types)
  3. What are the boundaries? (where does one concern end and another begin?)
  4. What crosses boundaries? (data types passed between modules)

  Example from your project:

  Requirement: "Process JSON from scraper and insert into database with validation"

  Decomposition:
  Verbs: parse, validate, check_existence, insert, transform
  Nouns: Company, Recruiter, Email, JSONData, ValidationResult

  Boundaries:
  ├─ Data Layer: knows about JSON structure, parsing
  ├─ Validation Layer: knows about business rules, not DB
  ├─ Database Layer: knows about DB operations, not JSON
  └─ Orchestration Layer: coordinates the above, knows the workflow

  Data that crosses boundaries:
  - Data → Validation: dict/object with company data
  - Validation → Database: validated dict + existence checks
  - Database → Orchestration: success/failure + created IDs

  Practice Exercise:
  - Take any feature requirement (1 sentence)
  - Spend 5 minutes listing: verbs, nouns, boundaries, crossing data
  - Show to AI: "validate this decomposition, suggest improvements"
  - Refine until it feels natural

  Success Metric: You can decompose any feature into 3-5 modules in <10 minutes

  ---
  Phase 2: Module Boundary → Interface Contract (The Bridge)

  Input: Module responsibilities
  Output: Function signatures WITHOUT implementation logic

  The Contract Template:
  # Module: [name]
  # Responsibility: [one sentence]
  # Dependencies: [what it needs from other modules]

  class ModuleName:
      """[why this exists, not how it works]"""

      def primary_operation(self, input: InputType) -> OutputType:
          """
          Does: [business outcome]
          Given: [preconditions]
          Returns: [postconditions]
          Errors: [failure modes]
          """
          ...

  Example:

  # Module: CompanyProcessor
  # Responsibility: Transform and validate company data for database insertion
  # Dependencies: None (pure business logic)

  class CompanyProcessor:
      """Validates company data meets minimum requirements before DB operations"""

      def validate_company_data(self, raw_data: dict) -> ValidationResult:
          """
          Does: Checks if company has enough information to be useful
          Given: Raw dict from JSON scraper
          Returns: ValidationResult(is_valid=bool, reason=str, cleaned_data=dict)
          Errors: Never raises, returns is_valid=False instead
          """
          ...

      def should_skip_company(self, validation: ValidationResult) -> bool:
          """
          Does: Decides if company should be marked as "NoInfo"
          Given: ValidationResult from validate_company_data
          Returns: True if insufficient data, False if processable
          Errors: None
          """
          ...

  The Key Rules:
  1. Types only, no logic (what goes in, what comes out)
  2. Preconditions/postconditions (contracts, not algorithms)
  3. Error modes (what can go wrong, not how to handle)
  4. One responsibility per function (if you write "and" in the docstring, split it)

  Practice Exercise:
  - Take your module boundaries from Phase 1
  - Write interface contracts for each module (3-5 functions per module)
  - Critical: Don't write ANY implementation logic, just signatures
  - Give to AI: "review these contracts for cohesion and coupling"

  Success Metric: You can write interface contracts that AI doesn't ask for clarification about

  ---
  Phase 3: Interface Contract → Data Flow Specification (Still Your Design Work)

  Input: Interface contracts from all modules
  Output: How data flows through the system

  The Flow Template:
  Workflow: [name]
  Trigger: [what starts this]

  Step 1: [Module.function](input) → output
    ├─ Success: proceed to Step 2
    └─ Failure: [what happens]

  Step 2: [Module.function](output_from_step_1) → output
    ├─ Success: proceed to Step 3
    └─ Failure: [what happens]

  Error Handling Strategy: [per-item skip | whole batch fail | retry]
  State Changes: [what gets updated when]

  Example:

  Workflow: Process Single Company from JSON
  Trigger: For each company object in JSON array

  Step 1: CompanyProcessor.validate_company_data(raw_company_dict) → ValidationResult
    ├─ Success (is_valid=True): proceed to Step 2
    └─ Failure (is_valid=False): mark company as "NoInfo", skip this company, continue to next

  Step 2: DatabaseService.check_company_exists(cleaned_data["cname"]) → Company | None
    ├─ Exists: use existing company, proceed to Step 3
    └─ Not exists: DatabaseService.insert_company(cleaned_data) → Company, proceed to Step 3

  Step 3: For each email in company_data["emails"]:
          EmailProcessor.validate_email(email_dict) → ValidationResult
          ├─ Valid: DatabaseService.check_email_exists_anywhere(email) → bool
          │   ├─ Exists: skip this email
          │   └─ Not exists: DatabaseService.insert_email(company.id, email_dict) → Email
          └─ Invalid: skip this email, log warning

  Step 4: For each recruiter in company_data["recruiters"]:
          RecruiterProcessor.validate_recruiter(recruiter_dict) → ValidationResult
          ├─ Valid AND (has_email OR has_linkedin): proceed to insert
          │   └─ DatabaseService.insert_recruiter_with_emails(company.id, recruiter_dict)
          └─ Invalid OR (no_email AND no_linkedin): skip this recruiter

  Error Handling: Skip individual items, continue processing batch
  State Changes: contact_status updated per company as they're processed
  Transaction Boundary: Commit per company (not per email/recruiter)

  The Key Rules:
  1. Linear flow (no nested logic, just sequence)
  2. Decision points explicit (success/failure paths)
  3. Error strategy declared (not implemented)
  4. State changes noted (when does DB state change)

  Practice Exercise:
  - Take your interface contracts from Phase 2
  - Write the data flow for one complete workflow
  - Use actual function signatures from Phase 2
  - Give to AI: "identify missing error cases or edge cases"

  Success Metric: The flow is complete enough that someone could implement it without asking "what do I do when..."

  ---
  Phase 4: Hand-off to AI (Implementation)

  What You Provide:
  Context Package:
  ├─ Module interfaces (Phase 2)
  ├─ Data flow specification (Phase 3)
  ├─ Domain constraints (from CLAUDE.md)
  └─ Example data (sample JSON, expected outputs)

  What You DON'T Provide:
  - Implementation details
  - Algorithm choices
  - Specific library calls
  - Code structure beyond interfaces

  The Prompt Pattern:
  I have designed the following system. Implement [Module/Workflow].

  ## Interfaces
  [paste from Phase 2]

  ## Data Flow
  [paste from Phase 3]

  ## Domain Constraints
  [relevant rules from CLAUDE.md]

  ## Example
  Input: [sample data]
  Expected Output: [expected result]

  Implement [specific module or workflow] following the interfaces exactly.
  Use [libraries/frameworks you've chosen].

  Practice Exercise:
  - Use your Phase 2 + 3 outputs
  - Prompt AI to implement ONE module
  - Evaluate: Did AI ask for clarification? Did it follow contracts?
  - Refine your Phase 2/3 outputs based on what was unclear

  Success Metric: AI implements correctly on first try, or asks intelligent clarifying questions (not basic ones)

  ---
  The Iterative Practice Loop

  Micro-Loop (Per Module)

  1. Decompose requirement → modules (5 min)
  2. Write interface contract for 1 module (10 min)
  3. Write data flow involving that module (10 min)
  4. Prompt AI to implement (1 min)
  5. Evaluate output quality (5 min)
     ├─ Perfect: move to next module
     ├─ Needs clarification: what was missing from contract/flow?
     └─ Wrong: was decomposition wrong?
  6. Update your contract/flow templates based on learnings

  Total cycle: ~30 minutes per module

  Macro-Loop (Per Feature)

  1. Pick feature from CLAUDE.md (your JSON processing pipeline)
  2. Do full decomposition (Phase 1)
  3. Write ALL interface contracts (Phase 2)
  4. Write complete data flow (Phase 3)
  5. Implement with AI module-by-module
  6. Test integration
  7. Reflect: Which phase was weakest? Where did AI struggle?
  8. Create template from what worked
  9. Pick similar feature, apply template, measure improvement

  Total cycle: 2-4 hours for medium feature

  ---
  Progressive Skill Building

  Week 1-2: Master Phase 2 (Interface Contracts)

  Exercise Set:
  - Write interface contracts for 10 different modules (unrelated to your project)
  - Examples:
    - EmailValidator
    - RateLimiter
    - TemplateRenderer
    - CacheManager
    - EventLogger
  - Practice: name functions clearly, define types precisely, document contracts
  - Validation: Give to AI, ask "what's ambiguous or missing?"

  Goal: Develop intuition for "complete" interface contracts

  Week 3-4: Master Phase 3 (Data Flow)

  Exercise Set:
  - Write data flows for 10 different workflows
  - Examples:
    - User registration with email verification
    - File upload with virus scanning
    - Payment processing with retries
    - Data import with validation
    - Multi-step form with persistence
  - Practice: explicit decision points, error paths, state changes
  - Validation: Implement yourself (no AI) to find gaps

  Goal: Learn to think in flows, not algorithms

  Week 5-6: Master Phase 1 (Decomposition)

  Exercise Set:
  - Take 10 feature requests (make them up or use GitHub issues)
  - Decompose into modules in 5 minutes each
  - Practice: finding boundaries, naming modules, identifying crossing data
  - Validation: Compare your decomposition to actual codebases (open source)

  Goal: Fast, intuitive decomposition that aligns with standard patterns

  Week 7-8: Integration & Templates

  Exercise Set:
  - Build 3 small features end-to-end using your framework
  - Create reusable templates for common patterns:
    - Data validation module
    - Database service module
    - Workflow orchestrator module
    - External API client module
  - Test templates on new features

  Goal: Fast design-to-code with consistent quality

  ---
  Quality Metrics (Instead of Time)

  Phase 2 Quality (Interface Contracts)

  - Completeness: AI implements without asking for missing info
  - Clarity: Function names are self-documenting
  - Precision: Types capture all valid inputs/outputs
  - Cohesion: Each function has one clear responsibility

  Phase 3 Quality (Data Flow)

  - Completeness: All error paths defined
  - Consistency: State changes are explicit
  - Testability: Each step is independently verifiable
  - Resilience: Failure modes don't cascade

  Phase 1 Quality (Decomposition)

  - Separation of Concerns: Each module has one reason to change
  - Low Coupling: Modules depend on interfaces, not implementations
  - High Cohesion: Everything in a module relates to its responsibility
  - Standard Patterns: Recognizable as common architectural patterns

  Overall System Quality

  - First-Time Success Rate: % of AI implementations that work without revision
  - Clarification Questions: Fewer = better contracts
  - Integration Bugs: Bugs at module boundaries = decomposition issues
  - Consistency: Similar features have similar structure

  ---
  Your Immediate Practice Plan

  This Week: Interface Contract Bootcamp

  Day 1:
  - Take your "CompanyProcessor" from your project
  - Write complete interface contract (Phase 2 only)
  - Give to AI: "review this contract, what's missing?"
  - Refine until AI says it's complete

  Day 2:
  - Write interface contracts for: RecruiterProcessor, EmailProcessor, DatabaseService
  - Don't implement, just contracts
  - Review for consistency (do they feel like they belong together?)

  Day 3:
  - Take someone else's feature (open source project)
  - Write interface contracts for their modules
  - Compare to their actual code
  - What did you miss? What did you over-specify?

  Day 4:
  - Create a template for interface contracts
  - Apply to 3 new modules (not from your project)
  - Test: give contracts to AI, ask it to implement

  Day 5:
  - Reflect: what makes a "good" contract?
  - Document your personal guidelines
  - Update your template

  Next Week: Data Flow Bootcamp

  (Follow same pattern for Phase 3)

  Week 3: Apply to Your Project

  - Use your templates to design the JSON processing pipeline
  - Full Phase 1-2-3
  - Implement with AI
  - Measure quality metrics
  - Refine templates

  ---
  The Balance You're Looking For

  You Provide:
  - WHAT each module does (responsibility)
  - WHAT goes in and out (types, contracts)
  - WHAT happens when (data flow, decisions)
  - WHAT the rules are (business constraints)

  AI Figures Out:
  - HOW to implement each function (algorithms)
  - HOW to structure the code (patterns, idioms)
  - HOW to handle edge cases (defensive programming)
  - HOW to optimize (performance, readability)

  The Boundary:
  If you can explain it without writing code → you specify it
  If it requires code to explain → let AI decide

  Example:
  - You: "Function validates email format" ← your spec
  - AI: Uses regex vs library vs custom parser ← AI decides
  - You: "Check email in both tables" ← your spec
  - AI: Query optimization, caching, parallel vs sequential ← AI decides