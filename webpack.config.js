const path = require('path');

module.exports = {
  entry: './frontend/src/index.js', // Entry point for your React app
  output: {
    path: path.resolve(__dirname, 'static/js'), // Output to Django's static directory
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.css$/, // Match .css files
        use: [
          "style-loader", // Injects styles into the DOM
          "css-loader",   // Resolves CSS imports
        ],
      },
      {
        test: /\.jsx?$/, // Transpile .js and .jsx files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'], // Resolve .js and .jsx files
  },
  mode: 'development', // Change to 'production' for production builds
};