const express = require('express');
const predictRouter = require('./predict.route');

const router = express.Router();

router.use('/predict', predictRouter);

module.exports = router;