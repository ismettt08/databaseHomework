#DATABASE_URL="postgres://taha:123456@127.0.0.1:5432/eczanem" python3 server.py

from flask import Flask
import views

def create_app():
    app = Flask(__name__)

    #app.config["DEBUG"] = True

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/login_api", view_func=views.login_api, methods=['POST'])
    app.add_url_rule("/logout_page", view_func=views.logout_page)
    app.add_url_rule("/employee", view_func=views.employee_page)
    app.add_url_rule("/register_api", view_func=views.register_api, methods=['POST'])
    app.add_url_rule("/sell", view_func=views.sell_page)
    app.add_url_rule("/addmed_api", view_func=views.addmed_api, methods=['POST'])
    app.add_url_rule("/addstock_api", view_func=views.addstock_api, methods=['POST'])
    app.add_url_rule("/updateAmount", view_func=views.update_medicine, methods=['POST', 'GET'])
    app.add_url_rule("/patient_table", view_func=views.patient_table)
    app.add_url_rule("/patient", view_func=views.patient, methods=['POST', 'GET'])
    app.add_url_rule("/med", view_func=views.med, methods=['POST', 'GET'])
    app.add_url_rule("/crud_patient", view_func=views.crud_patient, methods=['POST'])
    app.add_url_rule("/med_table", view_func=views.med_table)
    app.add_url_rule("/sale_table", view_func=views.sale_table)
    app.add_url_rule("/profile", view_func=views.profile)
    app.add_url_rule("/delete_account", view_func=views.delete_account)
    app.add_url_rule("/reports", view_func=views.reports)
    return app
