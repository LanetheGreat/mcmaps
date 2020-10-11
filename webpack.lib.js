const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const LodashPlugin = require('lodash-webpack-plugin');
const path = require('path');
const webpack = require('webpack');
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
    bail: true,
    context: __dirname,
    devtool: isDev ? 'inline-source-map' : 'source-map',
    entry: ['./assets/js/polyfills.js', './lib/index.js'],
    mode: isDev ? 'development' : 'production',
    module: {
        rules: [
            {
                test: /\.js$/i,
                include: /(assets\/js|assets\\js)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        plugins: [
                            '@babel/plugin-syntax-dynamic-import', // add support for dynamic imports
                            'lodash', // Tree-shake lodash
                        ],
                        presets: [
                            ['@babel/preset-env', {
                                loose: true, // Enable "loose" transformations for any plugins in this preset that allow them
                                modules: false, // Don't transform modules; needed for tree-shaking
                                useBuiltIns: 'entry',
                                targets: '> 1%, last 2 versions, Firefox ESR',
                                corejs: '^3.6.5',
                            }],
                        ],
                    },
                },
            },
            {
                test: require.resolve('jquery'),
                use: [{
                    loader: 'expose-loader',
                    options: '$',
                }],
            },
        ],
    },
    output: {
        filename: 'mcmaps.lib.js',
        path: path.resolve(__dirname, 'assets', 'dist'),
    },
    plugins: [
        new LodashPlugin(), // Complements babel-plugin-lodash by shrinking its cherry-picked builds further.
        new webpack.ProvidePlugin({ // Provide jquery automatically without explicit import
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery',
        }),
        new BundleAnalyzerPlugin({
            analyzerMode: 'static',
            openAnalyzer: false,
        }),
    ],
    resolve: {
        alias: {
            jquery: path.resolve(__dirname, 'node_modules', 'jquery', 'dist', 'jquery.min.js'),
        },
    },
};

if (isDev)
    module.exports.performance = { hints: false };
else
    module.exports.optimization = { noEmitOnErrors: true };
