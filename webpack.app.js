const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const LodashPlugin = require('lodash-webpack-plugin');
const path = require('path');
const webpack = require('webpack');
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
    bail: true,
    context: __dirname,
    devtool: isDev ? 'inline-source-map' : 'source-map',
    entry: [
        './assets/js/polyfills.js',
        './assets/js/mcmaps.js',
        './assets/scss/theme.scss',
    ],
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
                loader: 'expose-loader',
                options: {exposes: ['$', 'jQuery']},
            },
            {
                test: require.resolve('jquery.ajaxq'),
                use: 'imports-loader?wrapper=window',
            },
            {
                test: /\.(s[ac]|c)ss$/i,
                loader: [
                    isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
                    'css-loader',
                    {
                        loader: 'sass-loader',
                        options: {sourceMap: isDev},
                    },
                ],
            },
        ],
    },
    output: {
        chunkFilename: 'mcmaps-theme.[id].js',
        filename: 'mcmaps-theme.js',
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
        new MiniCssExtractPlugin({
            filename: 'mcmaps-theme.css',
        }),
    ],
};

if (isDev)
    module.exports.performance = { hints: false };
else
    module.exports.optimization = { noEmitOnErrors: true };
