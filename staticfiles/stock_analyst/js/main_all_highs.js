(async function() {
  try {
    // Fetch data from live API endpoint
    const response = await fetch('/main/data_stream');
    const data = await response.json();

    // Convert the data object to arrays for Chart.js
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const highs = companies.map(company => company.high);

    new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Stock High Prices ($)',
              data: highs,
              backgroundColor: [
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 205, 86, 0.8)'
              ],
              borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(255, 99, 132, 1)',
                'rgba(255, 205, 86, 1)'
              ],
              borderWidth: 2
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock High Prices by Company'
            },
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Price ($)'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Company'
              }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading stock data:', error);
  }
})();
// TODO: catch error and display error graphic if there's a data problem


//(async function() {
//  // Mock stock data - replace this with server call later
//  const stockData = [
//    { date: '2024-01', high: 152.30 },
//    { date: '2024-02', high: 168.45 },
//    { date: '2024-03', high: 145.20 },
//    { date: '2024-04', high: 175.80 },
//    { date: '2024-05', high: 189.95 },
//    { date: '2024-06', high: 201.15 },
//    { date: '2024-07', high: 194.70 },
//    { date: '2024-08', high: 210.45 },
//    { date: '2024-09', high: 225.30 },
//    { date: '2024-10', high: 218.85 },
//    { date: '2024-11', high: 235.60 },
//    { date: '2024-12', high: 248.90 }
//  ];
//
//  new Chart(
//    document.getElementById('main_highs'),
//    {
//      type: 'line',
//      data: {
//        labels: stockData.map(row => row.date),
//        datasets: [
//          {
//            label: 'Monthly Stock Highs ($)',
//            data: stockData.map(row => row.high),
//            borderColor: '#4CAF50',
//            backgroundColor: 'rgba(76, 175, 80, 0.1)',
//            tension: 0.3,
//            fill: true
//          }
//        ]
//      },
//      options: {
//        responsive: true,
//        plugins: {
//          title: {
//            display: true,
//            text: 'Stock All-Time Monthly Highs - 2024'
//          }
//        },
//        scales: {
//          y: {
//            beginAtZero: false,
//            title: {
//              display: true,
//              text: 'Price ($)'
//            }
//          },
//          x: {
//            title: {
//              display: true,
//              text: 'Month'
//            }
//          }
//        }
//      }
//    }
//  );
//})();

