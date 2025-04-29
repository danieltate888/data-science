const express = require('express');
const router = express.Router();
const { predictController } = require('../controllers/predict.controller');

// POST /predict
router.post('/', predictController);

module.exports = router;