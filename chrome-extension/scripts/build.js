'use strict';

const webpack = require('webpack');
const config = require('../webpack.config.js')
const compiler = webpack(config);
compiler.run((err, stats) => {
    if (err) {
        console.log(err, stats);
    }
});
