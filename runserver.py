# json encoding
from vendor.json_encoder import AlchemyEncoder

from app.hello import app

app.json_encoder = AlchemyEncoder

app.run(host='0.0.0.0', debug=False)