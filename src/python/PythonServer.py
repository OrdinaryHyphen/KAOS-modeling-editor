# coding: utf-8
# This code is based on https://qiita.com/Pu-of-Parari/items/f3733f0ba48e1df50667


from flask import Flask
from flask import request, make_response, jsonify
from flask_cors import CORS, cross_origin
from TabTextIntoDOTFile import GoalModelConstructor
#from GoalModelConstructor import GoalModelConstructor


app = Flask(__name__)
CORS(app, support_credentials=True, responses={r"/*": {"origins": "*"}})


@app.route('/', methods = ['GET'])
@cross_origin(supports_credentials=True)
def index():
	return "get index"

@app.route("/parse", methods=['GET','POST'])
@cross_origin(supports_credentials=True)
def parse():
	data = request.get_json()
	text = data['post_text']
	
	print(text)
	constructor = GoalModelConstructor()
	res = constructor.analyzeSpecification(text)
	#res = text
	print(res)

	response = {'result': res}
	return make_response(jsonify(response))

if __name__ == '__main__':
	app.run(debug=True, port=5000, threaded=True)