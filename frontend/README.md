# AirPilot - AI Copilot for Flight Safety

A React frontend application for simulating AI-assisted flight safety scenarios. This project provides an interactive interface for pilots and aviation professionals to experience how AI Copilot technology could assist in critical flight situations.

## Features

- **Landing Page**: Dark radar-themed interface with animated elements
- **Live Flight Tracking**: Real-time flight data with animated ticker display
- **Flight Selection**: Interactive selection of historic flight incidents
- **AI Simulation**: Chat-based simulation of AI Copilot assistance
- **3D Globe Visualization**: Interactive globe with live flight markers
- **Responsive Design**: Optimized for desktop and tablet viewing

## AI-Powered Development

This project leverages **Google Gemini** for intelligent API integration and development assistance:

### API Integration Support
- **Live Flight Data**: Gemini helped identify and integrate the OpenSky Network API for real-time flight tracking
- **Rate Limit Solutions**: Assisted in implementing fallback strategies and caching mechanisms for API rate limits
- **Alternative APIs**: Provided recommendations for authenticated access and premium flight data sources

### Development Guidance
- **Code Optimization**: Suggested performance improvements for real-time data handling
- **Error Handling**: Helped implement robust error handling and fallback mechanisms
- **Best Practices**: Guided implementation of aviation industry standards and best practices

## API Limitations & Solutions

### Current Implementation
- **OpenSky Network API**: Free tier with rate limits (15 flights max)
- **Fallback Data**: Demo flight data when API is unavailable
- **Real-time Updates**: 30-second refresh intervals

### Recommended Improvements
- **Authenticated Access**: Upgrade to OpenSky Network premium tier for higher limits
- **Caching Strategy**: Implement local caching to reduce API calls
- **Alternative Sources**: Consider ADS-B Exchange or FlightAware APIs for enhanced data

## Video Background Credit

The landing page background video is generated using **Google Veo**, an AI-powered video generation tool.

## Getting Started

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Available Scripts

In the project directory, you can run:

#### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

#### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).
