'use strict';

const command = require('commander');
command
    .option('-m, --minify', 'Minify files')
    .parse(process.argv);
const webpack = require('webpack');
let config = require('../webpack.config.js')
if (command.minify) {
    config.plugins = [new webpack.optimize.UglifyJsPlugin()];
    let filename = config.output.filename;
    const len = filename.length;
    filename = filename.substr(0, len-3) + '.min' + filename.substr(len-3);
    config.output.filename = filename
}
const compiler = webpack(config);
compiler.run((err, stats) => {
    if (err) {
        console.log(err, stats);
    }
});

