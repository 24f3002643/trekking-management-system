from datetime import date

def refresh_trek_status(trek):
    if trek.status == "cancelled":
        return 
    today = date.today()
    if today < trek.start_date:
        new_status = 'upcoming'
    elif trek.start_date <= today <= trek.end_date:
        new_status = 'ongoing'
    else:
        new_status = 'completed'
    if trek.status != new_status:
        trek.status = new_status