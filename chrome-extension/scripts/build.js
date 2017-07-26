'use strict';

const command = require('commander');
command
    .option('-m, --minify', 'Minify files')
    .parse(process.argv);

let config = require('../webpack.config.js')
if (command.minify) {
    const UglifyEsPlugin = require('uglify-es-webpack-plugin');
    config.plugins = [new UglifyEsPlugin()];
    let filename = config.output.filename;
    const len = filename.length;
    filename = filename.substr(0, len-3) + '.min' + filename.substr(len-3);
    config.output.filename = filename
}

const webpack = require('webpack');
const compiler = webpack(config);
compiler.run((err, stats) => {
    if (err) {
        console.log(err, stats);
    }
});
