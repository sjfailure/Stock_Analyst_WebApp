# Stock Web Application

A simple web application for viewing stock market data, built with the Django framework.

## Table of Contents

- Features
- Installation
- Usage
- Contributing
- License
- Contact

## Features

**Responsive Display:** View real-time stock data on any device.

**Detailed Stock Information Display:** Easily navigate to view data for specific stocks.

## Installation

To run this application locally, follow these steps:

Clone the repository:

```bash
git clone https://github.com/sjfailure/Stock_Analyst_WebApp.git
cd Stock_Analyst_WebApp
```

Set up environment variables:

This project requires two environment variables:

`mvp_stock_app_security_key`: A secret key for Django. You can generate one online or create a random string.
`alpha_vantage_api_key`: Your API key for Alpha Vantage. Visit their website to get a free key.

Create a `.env` file in the root directory and add your keys like this:

```
mvp_stock_app_security_key=your_django_secret_key
alpha_vantage_api_key=your_alpha_vantage_api_key
```

Run the application:

```bash
python manage.py runserver
```

The application will be accessible at http://127.0.0.1:8000/main.

## Usage

Once the server is running, navigate to the application in your web browser. Use the graphics to select specific companies and view more detailed information.

## Contributing

This is currently a private project for personal development. While contributions aren't being actively sought, I am open to suggestions and advice. If you have any feedback, please feel free to open an issue or reach out directly.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

Stamos Martin - sj_martin2023@hotmail.com