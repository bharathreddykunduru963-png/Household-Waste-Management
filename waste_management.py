
import sqlite3
from datetime import date

# Connect to database
con = sqlite3.connect("waste_management.db")
cur = con.cursor()

# Create database table
cur.execute("""
CREATE TABLE IF NOT EXISTS waste_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id TEXT NOT NULL,
    plastic REAL,
    paper REAL,
    glass REAL,
    food_waste REAL,
    other_waste REAL,
    total_waste REAL,
    recyclable REAL,
    non_recyclable REAL,
    recorded_date TEXT
)
""")
con.commit()

# Waste categories using dictionary
waste_categories = {
    "Plastic": "recyclable",
    "Paper": "recyclable",
    "Glass": "recyclable",
    "Food Waste": "non-recyclable",
    "Other": "non-recyclable"
}


# Validate quantity input
def get_quantity(category):
    while True:
        try:
            quantity = float(input(category + " (kg): "))
            if quantity < 0:
                print("Quantity cannot be negative.")
            else:
                return quantity
        except ValueError:
            print("Enter a valid number.")


# Add household waste record
def add_record():
    household_id = input("Enter Household ID: ").strip()

    if not household_id:
        print("Household ID cannot be empty.")
        return

    waste = {}

    print("\nEnter waste quantities:")
    for category in waste_categories:
        waste[category] = get_quantity(category)

    total = sum(waste.values())

    recyclable = sum(
        waste[c] for c in waste_categories
        if waste_categories[c] == "recyclable"
    )

    non_recyclable = total - recyclable

    cur.execute("""
        INSERT INTO waste_records
        (household_id, plastic, paper, glass, food_waste,
         other_waste, total_waste, recyclable,
         non_recyclable, recorded_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        household_id,
        waste["Plastic"],
        waste["Paper"],
        waste["Glass"],
        waste["Food Waste"],
        waste["Other"],
        total,
        recyclable,
        non_recyclable,
        date.today().isoformat()
    ))
    con.commit()

    print("\n----- WASTE ANALYSIS RESULT -----")
    print("Household ID:", household_id)

    for category, quantity in waste.items():
        print(category + ":", round(quantity, 2), "kg")

    print("Total Waste:", round(total, 2), "kg")
    print("Recyclable Waste:", round(recyclable, 2), "kg")
    print("Non-Recyclable Waste:",
          round(non_recyclable, 2), "kg")
    print("Record saved successfully!")


# View all records
def view_records():
    cur.execute("SELECT * FROM waste_records ORDER BY id DESC")
    records = cur.fetchall()

    if not records:
        print("No records found.")
        return

    for r in records:
        print("\nRecord ID:", r[0])
        print("Household ID:", r[1])
        print("Plastic:", r[2], "kg")
        print("Paper:", r[3], "kg")
        print("Glass:", r[4], "kg")
        print("Food Waste:", r[5], "kg")
        print("Other Waste:", r[6], "kg")
        print("Total Waste:", r[7], "kg")
        print("Recyclable Waste:", r[8], "kg")
        print("Non-Recyclable Waste:", r[9], "kg")
        print("Date:", r[10])


# Generate monthly report
def monthly_report():
    try:
        month = int(input("Enter month (1-12): "))
        year = int(input("Enter year: "))

        if not 1 <= month <= 12 or year < 1:
            print("Invalid month or year.")
            return

        cur.execute("""
            SELECT COUNT(*), SUM(plastic), SUM(paper),
                   SUM(glass), SUM(food_waste), SUM(other_waste),
                   SUM(total_waste), SUM(recyclable),
                   SUM(non_recyclable)
            FROM waste_records
            WHERE substr(recorded_date, 1, 7) = ?
        """, (f"{year:04d}-{month:02d}",))

        r = cur.fetchone()

        if r[0] == 0:
            print("No records found for this month.")
            return

        categories = {
            "Plastic": r[1] or 0,
            "Paper": r[2] or 0,
            "Glass": r[3] or 0,
            "Food Waste": r[4] or 0,
            "Other": r[5] or 0
        }

        print("\n----- MONTHLY REPORT -----")
        print("Month:", month, "Year:", year)
        print("Household Records:", r[0])

        for category, quantity in categories.items():
            print(category + ":", round(quantity, 2), "kg")

        print("Total Waste:", round(r[6], 2), "kg")
        print("Recyclable Waste:", round(r[7], 2), "kg")
        print("Non-Recyclable Waste:", round(r[8], 2), "kg")

        if r[6] > 0:
            print("Recyclable Percentage:",
                  round(r[7] / r[6] * 100, 2), "%")
            print("Non-Recyclable Percentage:",
                  round(r[8] / r[6] * 100, 2), "%")

        print("Major Waste Category:",
              max(categories, key=categories.get))

        print("\nWaste Reduction Suggestions:")
        print("- Reduce single-use plastics.")
        print("- Reuse paper and glass.")
        print("- Compost food waste where possible.")
        print("- Separate waste at the source.")
        print("- Send recyclable items to authorized recyclers.")

    except ValueError:
        print("Enter a valid month and year.")


# Category-wise analysis
def category_analysis():
    cur.execute("""
        SELECT SUM(plastic), SUM(paper), SUM(glass),
               SUM(food_waste), SUM(other_waste)
        FROM waste_records
    """)
    r = cur.fetchone()

    if r[0] is None:
        print("No records available.")
        return

    categories = {
        "Plastic": r[0],
        "Paper": r[1],
        "Glass": r[2],
        "Food Waste": r[3],
        "Other": r[4]
    }

    total = sum(categories.values())
    recyclable = sum(categories[c] for c in
                     ["Plastic", "Paper", "Glass"])
    non_recyclable = total - recyclable

    print("\n----- CATEGORY-WISE ANALYSIS -----")
    for category, quantity in categories.items():
        percentage = quantity / total * 100 if total else 0
        print(category + ":", round(quantity, 2), "kg",
              "|", round(percentage, 2), "%")

    print("Total Waste:", round(total, 2), "kg")
    print("Recyclable Waste:", round(recyclable, 2), "kg")
    print("Non-Recyclable Waste:",
          round(non_recyclable, 2), "kg")

    print("Highest Waste Category:",
          max(categories, key=categories.get))


# Main menu
def main():
    while True:
        print("\n===== HOUSEHOLD WASTE MANAGEMENT =====")
        print("1. Add Household Waste Record")
        print("2. View All Records")
        print("3. Generate Monthly Report")
        print("4. Category-Wise Analysis")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_record()
        elif choice == "2":
            view_records()
        elif choice == "3":
            monthly_report()
        elif choice == "4":
            category_analysis()
        elif choice == "5":
            print("Thank you for using the system!")
            break
        else:
            print("Invalid choice. Select 1-5.")


try:
    main()
finally:
    con.close()
