const UglifyEsPlugin = require('uglify-es-webpack-plugin');

module.exports = {
    entry: {
        'popup': './src/js/popup.js',
        'options': './src/js/options.js'
    },
    plugins: [new UglifyEsPlugin()],
    output: {
        path: __dirname + '/dist/',
        filename: './js/[name].min.js'
    }
};
