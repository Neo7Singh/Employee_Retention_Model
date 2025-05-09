from wsgiref import simple_server
from flask import Flask, request, render_template
from flask import Response
import flask_monitoringdashboard as dashboard
import pandas as pd
from flask_cors import CORS, cross_origin
from apps.training.train_model import TrainModel
from apps.prediction.predict_model import PredictModel
from apps.core.config import Config

app = Flask(__name__)
dashboard.bind(app)
CORS(app)

@app.route('/', methods=['POST','GET'])
def index_page():
    return render_template('index.html')



@app.route('/training', methods=['POST'])
@cross_origin()
def training_route_client():
    try:
        config = Config()
        #get run id
        run_id = config.get_run_id()
        data_path = config.training_data_path
        #trainmodel object initialization
        trainmodel=TrainModel(run_id,data_path)
        #training the model
        trainmodel.training_model()
        return Response("Training successfull! and its RunID is : "+str(run_id))
    except ValueError:
        return Response("Error Occurred! %s" % ValueError)
    except KeyError:
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" % e)

@app.route('/batchprediction', methods=['POST'])
@cross_origin()
def batch_prediction_route_client():
    try:
        config = Config()
        #get run id
        run_id = config.get_run_id()
        data_path = config.prediction_data_path
        #prediction object initialization
        predictmodel=PredictModel(run_id, data_path)
        #prediction the model
        predictmodel.batch_predict_from_model()
        return Response("Prediction successfull! and its RunID is : "+str(run_id))
    except ValueError:
        return Response("Error Occurred! %s" % ValueError)
    except KeyError:
        return Response("Error Occurred! %s" % KeyError)
    except Exception as e:
        return Response("Error Occurred! %s" % e)


@app.route('/prediction', methods=['POST'])
@cross_origin()
def single_prediction_route_client():
    try:
        config = Config()
        run_id = config.get_run_id()
        data_path = config.prediction_data_path
        print('Test')

        if request.method == 'POST':
            print("Content-Type:", request.content_type)

            if request.content_type == 'application/x-www-form-urlencoded':
                data = request.form.to_dict()
                print("Received form data:", data)

                satisfaction_level = data.get('satisfaction_level')
                last_evaluation = data.get("last_evaluation")
                number_project = data.get("number_project")
                average_montly_hours = data.get("average_montly_hours")
                time_spend_company = data.get("time_spend_company")
                work_accident = data.get("Work_accident")
                promotion_last_5years = data.get("promotion_last_5years")
                salary = data.get("salary")

                required_fields = [
                    satisfaction_level,
                    last_evaluation,
                    number_project,
                    average_montly_hours,
                    time_spend_company,
                    work_accident,
                    promotion_last_5years,
                    salary
                ]

                if any(field is None or field == '' for field in required_fields):
                    return Response("Error: Missing one or more required fields.", status=400)

                data = pd.DataFrame(data=[[0, satisfaction_level, last_evaluation, number_project, average_montly_hours, time_spend_company, work_accident, promotion_last_5years, salary]],
                                    columns=['empid', 'satisfaction_level', 'last_evaluation', 'number_project', 'average_montly_hours', 'time_spend_company', 'Work_accident', 'promotion_last_5years', 'salary'])

                convert_dict = {
                    'empid': int,
                    'satisfaction_level': float,
                    'last_evaluation': float,
                    'number_project': int,
                    'average_montly_hours': int,
                    'time_spend_company': int,
                    'Work_accident': int,
                    'promotion_last_5years': int,
                    'salary': object
                }

                data = data.astype(convert_dict)

                predictModel = PredictModel(run_id, data_path)
                output = predictModel.single_predict_from_model(data)
                print('output : ' + str(output))
                return Response("Predicted Output is : " + str(output))
            else:
                return Response("Error: Request must be form-encoded.", status=400)
    except ValueError as ve:
        return Response("ValueError Occurred! %s" % str(ve), status=400)
    except KeyError as ke:
        return Response("KeyError Occurred! %s" % str(ke), status=400)
    except Exception as e:
        return Response("Error Occurred! %s" % str(e), status=500)

if __name__ == "__main__":
    #app.run()
    host = '0.0.0.0'
    port = 5000
    httpd = simple_server.make_server(host, port, app)
    httpd.serve_forever()