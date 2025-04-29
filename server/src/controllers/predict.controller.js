const axios = require('axios');

const predictController = async (req, res) => {
    try {
        const response = await axios.post('http://localhost:6000/predict', req.body);
        res.json(response.data);
    } catch (error) {
        console.error('Error calling FastAPI:', error.message);
        if (error.response) {
            res.status(error.response.status).json(error.response.data);
        } else {
            res.status(500).json({ message: 'Internal Server Error' });
        }
    }
};

module.exports = {
    predictController,
};