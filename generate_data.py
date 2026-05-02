"""
generate_data.py — Generate synthetic Canadian/North American transaction dataset
Run with: python generate_data.py
"""

import csv
import random
from pathlib import Path

random.seed(42)

TRANSACTIONS = {

    "food": [
        "Tim Hortons #1234", "Tim Hortons #5678", "Starbucks #3421",
        "Starbucks Coffee Vancouver", "Second Cup Coffee", "Blenz Coffee SFU",
        "Blenz Coffee Burnaby", "JJ Bean Coffee Roasters", "Waves Coffee House",
        "Revolver Coffee Vancouver", "49th Parallel Coffee", "Matchstick Coffee",
        "Nemesis Coffee", "Propaganda Coffee", "Bean Around The World",
        "ethical bean coffee", "Analog Coffee", "Nelson The Seagull",
        "The Keg Steakhouse Vancouver", "Earl's Kitchen Vancouver",
        "White Spot Restaurant", "A&W Restaurant #234", "A&W Canada #567",
        "McDonald's #12135", "McDonald's #4521", "Burger King #234",
        "Wendy's #456", "Subway #1234", "Subway Restaurant",
        "Boston Pizza Vancouver", "Cactus Club Cafe", "Cactus Club Metrotown",
        "Moxie's Grill Vancouver", "Browns Socialhouse", "Joey Restaurant",
        "Milestones Restaurant", "Earls Kitchen Burnaby",
        "Nando's Chicken Vancouver", "Five Guys Burgers Vancouver",
        "Freshii Vancouver", "Chipotle Mexican Grill",
        "Sushi Garden Burnaby", "Sushi Village Whistler", "Guu Japanese Restaurant",
        "Kingyo Izakaya", "Zakkushi Charcoal Grill", "Steve's Poke Bar",
        "Pokéworks Vancouver", "Poke Time", "Ramen Danbo Vancouver",
        "Marutama Ramen", "Santouka Ramen", "Kintaro Ramen",
        "Bao Bei Chinese Brasserie", "Peaceful Restaurant",
        "Phnom Penh Restaurant", "Pho Thanh Long", "Pho Bich Nga",
        "Thai Orchid Restaurant", "Maenam Thai Restaurant",
        "Vij's Restaurant", "Medina Cafe Vancouver", "Cafe Medina",
        "Tst Broye Cafe Hornb", "Shipyards Coffee",
        "Echo Cafe Brunch", "The Bread Quarter",
        "Lumine Coffee Vancouver", "Sq Simit Kitsilano",
        "Nuba Restaurant", "The Naam Vegetarian",
        "Uber Eats", "Skip The Dishes", "DoorDash",
        "Uber Canada/Ubereats", "Skipthedishes.com",
        "Taco Bell #234", "KFC #456", "Pizza Hut #789",
        "Domino's Pizza", "Little Caesars Pizza",
        "Dairy Queen #234", "Harvey's Restaurant", "Swiss Chalet",
        "Body Energy Club", "Jugo Juice", "Booster Juice",
        "Pressed Juicery", "Juice Truck Vancouver",
        "Fsm 1045", "Blenz Sfu Burnaby",
        "Oscars Smoke Shop", "Sp The Candy Room",
        "Olde Tyme Candy Shoppe",
    ],

    "groceries": [
        "Safeway #4911", "Safeway #1234", "Safeway Burnaby",
        "Save On Foods #234", "Save On Foods Burnaby", "Save On Foods Metrotown",
        "Real Canadian Superstore", "Superstore #234",
        "No Frills #456", "FreshCo #789", "FreshCo Burnaby",
        "Loblaws #234", "Loblaws City Market",
        "Metro Grocery #456", "IGA Marketplace", "IGA #234",
        "Nesters Market 4548", "Nesters Market Vancouver",
        "Choices Markets", "Choices Market Kitsilano",
        "Whole Foods Market Vancouver", "Whole Foods #234",
        "T&T Supermarket Burnaby", "T&T Supermarket Richmond",
        "T&T Supermarket Metrotown", "T&T Supermarket",
        "H Mart Vancouver", "H Mart Coquitlam",
        "Osaka Supermarket", "Fujiya Japanese Foods",
        "Persia Foods", "Kin's Farm Market",
        "Donald's Market", "Stong's Market",
        "Costco Wholesale #234", "Costco Wholesale Burnaby",
        "Costco Wholesale Richmond",
        "7-Eleven #1234", "7-Eleven Vancouver",
        "Mac's Convenience Store", "Circle K #234",
    ],

    "transport": [
        "Translink Compass Card", "Caconnect Ryanv Vnlc2",
        "Caconnect Ryan Vend", "BC Transit Victoria",
        "West Coast Express", "Skytrain Compass",
        "Uber Canada/Ubertrip", "Uber Trip",
        "Lyft *Ride", "Lyft *Ride Sat 2pm", "Lyft Vancouver",
        "Enterprise Rent A Car", "Hertz Car Rental",
        "Budget Car Rental", "Avis Car Rental",
        "Zipcar Vancouver", "Evo Car Share", "Modo Car Share",
        "Petro Canada #1234", "Petro Canada Burnaby",
        "Shell Gas Station #234", "Shell Canada",
        "Esso Gas Station", "Chevron Gas Station",
        "Husky Gas Station", "Canadian Tire Gas Bar",
        "Impark Parking", "Honk Parking",
        "City Of Vancouver Parking",
        "Air Canada", "WestJet Airlines",
        "BC Ferries", "Pacific Coach Lines",
        "Yellow Cab Vancouver", "MacLure's Cabs",
    ],

    "shopping": [
        "Aritzia Pacific Ctr 10", "Aritzia Robson Street",
        "Aritzia Metrotown", "Aritzia Vancouver",
        "Lululemon #234", "Lululemon Athletica",
        "Arc'teryx Vancouver", "Roots Canada #234",
        "Club Monaco", "Banana Republic #234",
        "H&M #234 Canada", "Zara #234 Vancouver",
        "Uniqlo Vancouver", "Uniqlo Metrotown",
        "Forever 21 #234", "Urban Outfitters Vancouver",
        "American Eagle #234", "Winners #234 Burnaby",
        "TK Maxx", "Marshalls #234",
        "Sport Chek #234", "Sport Chek Metrotown",
        "MEC Mountain Equipment",
        "Swarovski Metrotown", "Pandora #234",
        "Michael Kors #234", "Coach #234",
        "Hudson's Bay #234", "Hudson's Bay Metrotown",
        "Nordstrom Vancouver", "Simons #234",
        "Holt Renfrew Vancouver",
        "Amazon.ca", "Amazon Prime", "Amazon Marketplace",
        "Best Buy #234 Burnaby", "Best Buy Canada",
        "London Drugs Electronics",
        "SFU Bookstore Spirit Shop", "UBC Bookstore",
        "Indigo Books #234", "Chapters Indigo",
        "Dollarama #234", "Dollar Tree #234",
        "Miniso #234", "Daiso Japan Vancouver",
        "Ikea Coquitlam", "Ikea Richmond",
        "Canadian Tire #234", "Canadian Tire Burnaby",
        "Walmart #234 Canada",
    ],

    "healthcare": [
        "Shoppers Drug Mart #22", "Shoppers Drug Mart #234",
        "Shoppers Drug Mart Burnaby", "Shoppers Drug Mart Metrotown",
        "London Drugs #234", "London Drugs Burnaby",
        "Rexall Pharmacy #234", "Pharmasave #234",
        "Guardian Pharmacy", "Medicine Shoppe Pharmacy",
        "Vancouver General Hospital", "BC Children's Hospital",
        "St Paul's Hospital", "Burnaby Hospital",
        "Medical Clinic Vancouver", "Urgent Care Centre",
        "Walk In Clinic Burnaby", "Medicentres Canada",
        "Lifemark Health", "Copeman Healthcare",
        "Pacific Dental Centre", "Vancouver Dental",
        "Burnaby Dental Group", "Metrotown Dental",
        "Clearly #234", "Clearly Contacts",
        "Lens Crafters #234", "Eye Care Centre",
        "GNC #234", "Popeyes Supplements",
        "Nature's Fare Markets",
    ],

    "subscriptions": [
        "Netflix", "Netflix.com", "Netflix Subscription",
        "Spotify", "Spotify Premium", "Spotify Ab",
        "Apple Music", "Apple One", "Apple TV+",
        "Disney+ Canada", "Disney Plus",
        "Amazon Prime Video", "Amazon Prime Membership",
        "Crave TV", "CBC Gem",
        "YouTube Premium", "Google One",
        "Adobe Creative Cloud", "Adobe Systems",
        "Microsoft 365", "Microsoft Office",
        "Dropbox Plus", "Google Storage", "iCloud Storage",
        "Notion.so", "Zoom Video", "ChatGPT Plus",
        "Github Pro", "Figma",
        "Globe And Mail", "Vancouver Sun Digital",
        "Tinder Gold", "Bumble Boost", "Hinge Premium",
        "Xbox Game Pass", "PlayStation Network",
        "Nintendo Online", "Steam Purchase",
    ],

    "utilities": [
        "BC Hydro #234", "BC Hydro Payment",
        "Fortis BC Gas", "FortisBC Energy",
        "City Of Vancouver Water",
        "Telus Communications", "Telus Internet",
        "Telus Mobility", "Telus Home Security",
        "Rogers Communications", "Rogers Wireless",
        "Rogers Internet #234", "Shaw Communications",
        "Shaw Cable #234", "Shaw Internet",
        "Bell Canada", "Bell Mobility",
        "Fido Mobile", "Koodo Mobile",
        "Public Mobile", "Freedom Mobile",
        "Virgin Plus Canada",
        "ICBC Insurance", "ICBC Autoplan",
        "Blue Cross BC", "Pacific Blue Cross",
        "Manulife Financial", "Sun Life Financial",
        "Wawanesa Insurance", "Intact Insurance",
        "TD Insurance", "RBC Insurance",
    ],

    "health_fitness": [
        "Goodlife Fitness #234", "Goodlife Fitness Burnaby",
        "Steve Nash Fitness", "Anytime Fitness #234",
        "Equinox Vancouver", "Y M C A Vancouver",
        "YMCA Burnaby", "Fitness World #234",
        "Snap Fitness #234", "Orangetheory Fitness",
        "F45 Training Vancouver", "Barry's Bootcamp",
        "SoulCycle Vancouver", "Peloton Interactive",
        "Peloton Subscription", "YYoga Vancouver",
        "Modo Yoga #234", "Hot Yoga Vancouver",
        "Pure Yoga Vancouver", "Barre Body Studio",
        "City Of Vancouver Rec", "Burnaby Recreation",
        "Richmond Olympic Oval", "Hive Climbing Gym",
        "North Shore Climbing", "Running Room #234",
        "MEC Vancouver", "Altitude Sports",
    ],

    "education": [
        "SFU Burnaby Tuition", "SFU Simon Fraser University",
        "SFU Bookstore", "SFU Athletics",
        "UBC Vancouver Tuition", "UBC Bookstore",
        "BCIT Tuition", "Langara College",
        "Kwantlen Polytechnic", "Douglas College",
        "Capilano University", "Emily Carr University",
        "Coursera", "Udemy", "LinkedIn Learning",
        "Skillshare", "MasterClass",
        "Khan Academy", "Duolingo Plus",
        "Kumon Learning Centre", "Sylvan Learning",
        "Oxford Learning Centre",
        "Chegg Textbooks", "VitalSource Bookshelf",
    ],

    "transfers": [
        "Payment From - *****10*45",
        "E Transfer Received",
        "Interac E Transfer",
        "Customer Transfer Dr.",
        "Customer Transfer Cr.",
        "E Transfer Sent",
        "Wire Transfer",
        "Paypal Transfer",
        "Paypal *Transfer",
        "Bank Transfer",
        "Online Transfer",
    ],

    "income": [
        "Payroll Direct Deposit",
        "Employer Payroll",
        "Direct Deposit Payroll",
        "Employment Insurance",
        "EI Payment Canada",
        "CRA Tax Refund",
        "GST HST Credit",
        "BC Income Assistance",
        "Student Loan Deposit",
        "NSLSC Student Loan",
        "Bursary Deposit SFU",
        "Scholarship Deposit",
        "Freelance Payment",
    ],

    "cash": [
        "ATM Withdrawal #234",
        "ATM Withdrawal Burnaby",
        "ATM Cash Withdrawal",
        "Withdrawal",
        "Cash Withdrawal",
        "ATM Fee",
        "Bank ATM Withdrawal",
    ],
}


def generate_dataset(n_samples: int, output_path: str):
    rows = []
    categories = list(TRANSACTIONS.keys())
    samples_per_cat = n_samples // len(categories)
    remainder = n_samples % len(categories)

    for i, category in enumerate(categories):
        merchants = TRANSACTIONS[category]
        n = samples_per_cat + (1 if i < remainder else 0)
        for _ in range(n):
            merchant = random.choice(merchants)
            variations = [
                merchant,
                merchant.lower(),
                merchant.upper(),
                merchant + f" #{random.randint(100, 9999)}",
                merchant.replace("#", "").strip(),
            ]
            transaction_text = random.choice(variations)
            rows.append({"transaction_text": transaction_text, "category": category})

    random.shuffle(rows)
    Path(output_path).parent.mkdir(exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["transaction_text", "category"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ Generated {len(rows)} transactions → {output_path}")
    return len(rows)


if __name__ == "__main__":
    print("🇨🇦 Generating Canadian/North American transaction dataset...\n")
    generate_dataset(8000, "data/ca_train_transactions.csv")
    generate_dataset(1500, "data/ca_test_transactions.csv")
    print("\n✅ Done! Now run: python train_model.py")