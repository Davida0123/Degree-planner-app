# Degree-planner-app
An interactive degree planner designed to simplify university course mapping, featuring multi-term simulations, prerequisite validation, professor ratings and extensive course details.

# Design Decisions
* Determine if using Json or some relation database to store the courses
    * Decided on a relational database (PostgreSQL) as a degree's structure is inherently relational. We need to track different courses in diffrent subjects, the many major/minor/breadth requriements and how prerequisites are connected. PostgreSQL allows us to establish this network on the database level, maximizing call speed. The interconnected structure also allows dynamic querying and enforces referential integrity(error before deleting a course's prerequisite course). The ease of access with Supabase or firebase(free alternative githuib repo, requries more research) was also a determining factor.
    * Decided to start with a simple linear prerequisite model(just visual text prereq) and grow that into a complex logical tree that supports multi prerequisites down the line.

* Determine what language/tools we are going to use to scrape the data
    *
