const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const LodashPlugin = require('lodash-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');
const webpack = require('webpack');
const isDev = process.env.NODE_ENV === 'development';
const package = require('./package.json');

const devOptions = isDev ? {
    performance: {
        hints: false,
    }
} : {
    optimization: {
        noEmitOnErrors: true
    }
};

module.exports = {
    bail: true,
    context: __dirname,
    devServer: {
        contentBase: path.resolve(__dirname, 'assets', 'dist'),
        serveIndex: false,
        port: 3000,
        proxy: [{
            context: ['/api', '/cache'],
            target:'http://localhost:3001',
        }],
        publicPath: '/',
    },
    devtool: isDev ? 'inline-source-map' : 'source-map',
    entry: {
        '-theme': [
            './assets/js/polyfills.js',
            './assets/js/mcmaps.js',
            './assets/scss/theme.scss',
        ],
        '.lib': [
            './assets/js/polyfills.js',
            './lib/index.js',
        ],
    }
    ,
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
        chunkFilename: 'mcmaps[name].[id].js',
        filename: 'mcmaps[name].js',
        path: path.resolve(__dirname, 'assets', 'dist'),
        publicPath: '/',
    },
    plugins: [
        new HtmlWebpackPlugin({
            filename: 'index.html',
            inject: false,
            hash: true,
            template: 'index.dev.html',
            title: 'MC Maps Dev Server',
            version: package.version,
        }),
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
    ...devOptions,
};
