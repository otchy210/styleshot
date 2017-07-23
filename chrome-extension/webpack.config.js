module.exports = {
    entry: './src/js/entry.js',
    output: {
        path: __dirname + '/dist/',
        filename: './js/app.js'
    },
    module: {
        loaders: [{
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            query: {
                presets: ['es2015']
            }
        }]
    }
};
