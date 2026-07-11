import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


#Horizontal bar chart: top 10 treks by number of bookings
def make_top_treks_chart(top_treks):
    if not top_treks:
        return None
    names = [t["trekname"] for t in top_treks]
    counts = [t["count"] for t in top_treks]

    plt.figure(figsize=(7, 4))
    plt.barh(names[::-1], counts[::-1], color="#0d6efd")
    plt.xlabel("Number of Bookings")
    plt.ylabel("Trek Name")
    plt.title("Top 10 Popular Treks")
    plt.tight_layout()
    plt.savefig("static/charts/top_treks.png")
    plt.close()

    return "charts/top_treks.png"


# Pie chart: pending vs booked bookings.
def make_pending_booked_chart(pending_count, booked_count):

    if pending_count + booked_count == 0:
        return None

    plt.figure(figsize=(5, 5))
    plt.pie([pending_count, booked_count], labels=["Pending", "Booked"], autopct="%1.1f%%", startangle=90)
    plt.title("Bookings: Pending vs Booked")
    plt.tight_layout()
    plt.savefig("static/charts/booking_status.png")
    plt.close()
    return "charts/booking_status.png"


# Pie chart: staff approval status split.
def make_staff_approval_chart(approved, pending, rejected):
    if approved + pending + rejected == 0:
        return None

    plt.figure(figsize=(5, 5))
    plt.pie([approved, pending, rejected], labels=["Approved", "Pending", "Rejected"], autopct="%1.1f%%", startangle=90)
    plt.title("Staff Approval Status")
    plt.tight_layout()
    plt.savefig("static/charts/staff_approval.png")
    plt.close()
    return "charts/staff_approval.png"


# Bar chart: number of bookings per day, over the past 7 days.
def make_last_7_days_chart(last_7_days):
    if not last_7_days:
        return None

    labels = [d["date"].strftime("%d %b") for d in last_7_days]
    counts = [d["count"] for d in last_7_days]

    

    plt.figure(figsize=(7, 4))
    plt.bar(labels, counts, color="#0d6efd")
    plt.xlabel("Date")
    plt.ylabel("Bookings")
    plt.title("Bookings in the Past 7 Days")
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig("static/charts/last_7_days.png")
    plt.close()

    return "charts/last_7_days.png"


# Pie chart: active vs blacklisted trekkers.
def make_trekker_blacklist_chart(active, blacklisted):
    if active + blacklisted == 0:
        return None

    plt.figure(figsize=(5, 5))
    plt.pie([active, blacklisted], labels=["Active", "Blacklisted"], autopct="%1.1f%%", startangle=90)
    plt.title("Trekkers: Active vs Blacklisted")
    plt.tight_layout()
    plt.savefig("static/charts/trekker_blacklist.png")
    plt.close()
    return "charts/trekker_blacklist.png"



#Pie chart: active vs blacklisted staff.
def make_staff_blacklist_chart(active, blacklisted):
    
    if active + blacklisted == 0:
        return None

    plt.figure(figsize=(5, 5))
    plt.pie(
        [active, blacklisted],
        labels=["Active", "Blacklisted"],
        autopct="%1.1f%%",
        startangle=90
    )
    plt.title("Staff: Active vs Blacklisted")
    plt.tight_layout()
    plt.savefig("static/charts/staff_blacklist.png")
    plt.close()

    return "charts/staff_blacklist.png"