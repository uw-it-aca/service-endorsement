const path = require("path")
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const TerserJSPlugin = require('terser-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');


module.exports = {

    context: __dirname,

    entry: {
        main: ['./endorsement/static/endorsement/js/main.js', './endorsement/static/endorsement/css/critical.scss'],
        handlebars: ['./endorsement/static/endorsement/js/handlebars-helpers.js'],
        accept: ['./endorsement/static/endorsement/js/accept.js'],
        endorsee: ['./endorsement/static/endorsement/js/endorsee.js'],
        endorser: ['./endorsement/static/endorsement/js/endorser.js'],
        notifications: ['./endorsement/static/endorsement/js/notifications.js'],
        statistics: ['./endorsement/static/endorsement/js/statistics.js'],
        shared_proxy: ['./endorsement/static/endorsement/js/shared_proxy.js']
    },

    optimization: {
        minimizer: [new TerserJSPlugin({})],
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /node_modules/,
                    chunks: "initial",
                    name: "vendor",
                    priority: 10,
                    enforce: true
                }
            }
        }
    },

    output: {
        path: path.resolve('./endorsement/static/endorsement/bundles/'),
        filename: "[name]-[fullhash].js",
    },

    plugins: [
        new CleanWebpackPlugin(),
        new BundleTracker({
            filename: './endorsement/static/webpack-stats.json'
        }),
        new MiniCssExtractPlugin({
            filename: "[name]-[fullhash].css",
        })
    ],

    module: {
        rules: [{
                test: /\.s[ac]ss$/,
                use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"]
            },
            {
                test: /\.css$/,
                use: [MiniCssExtractPlugin.loader, "css-loader"]
            }
        ]
    },

    resolve: {
        extensions: ['\.js']
    }

}
