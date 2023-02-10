# Meal Planning with Python and Networkx

Not sure what to cook from a list of recipes? This notebook produces a plan for the days ahead, and emails you your shopping list.

It uses the networkx graphing package. Each meal is a node, and 'legal' edges exist between nodes if and only if the meals contain different proteins and carbohydrates.

Then, the code prompts you to select meals by traversing the graph along 'legal' edges.

Once your plan has been produced, a shopping list is produced.

The code prompts you to add on commonly bought staples (milk, eggs, bread...), and you can remove items which you already have in your kitchen.

I've used the yagmail package to send an email containing both the meal plan and shopping list. No more paper lists, and no more second-guessing which ingredients you planned to use on which day.

Feedback welcome. 

Further dev could include: 
- Integration with calendar apps
- Further restriction on weekend vs weekday meals (are leftovers needed for the following day's lunch?)
