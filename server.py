#DATABASE_URL="postgres://taha:123456@127.0.0.1:5432/eczanem" python3 server.py

from flask import Flask
import views

def create_app():
    app = Flask(__name__)

    app.config["DEBUG"] = True

    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/login_api", view_func=views.login_api, methods=['POST'])
    app.add_url_rule("/logout_page", view_func=views.logout_page)
    app.add_url_rule("/employee", view_func=views.employee_page)
    app.add_url_rule("/register_api", view_func=views.register_api, methods=['POST'])
    app.add_url_rule("/sell", view_func=views.sell_page)
    app.add_url_rule("/addmed_api", view_func=views.addmed_api, methods=['POST'])
    app.add_url_rule("/updateAmount", view_func=views.update_medicine, methods=['POST', 'GET'])
    app.add_url_rule("/patient_table", view_func=views.patient_table)
    app.add_url_rule("/patient", view_func=views.patient, methods=['POST', 'GET'])
    app.add_url_rule("/crud_patient", view_func=views.crud_patient, methods=['POST'])
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)

    """
    TODO LIST
    ->Add sell_page
        Hold medicine_basket array and use ninja(for) to write out
        Every redirect write out again
        Increasing/decreasing deleting/adding means reload
        Payment method is clickbox

        Add select customer section with autocomplete
        !Install every customer name to use in autocomplete


    ->Add report_page
        GROUP BY kullan
    """