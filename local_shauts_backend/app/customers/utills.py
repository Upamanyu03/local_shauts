from app.invoices.models import Invoice
from app.estimate.models import Estimate
from app import db

def update_table(table_name, id):
    if table_name=="Invoice":
        update = Invoice.query.filter_by(id=id).first()
    elif table_name=="Estimate":
        update = Estimate.query.filter_by(id=id).first()
    if update:
        if update.flag == 1:
            update.flag =0
        else:
            update.flag =1
        db.session.commit()