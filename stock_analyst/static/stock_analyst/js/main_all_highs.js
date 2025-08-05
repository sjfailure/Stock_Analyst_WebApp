fetch('/main/data_stream')
    .then(response => response.json())
    .then(data => {
        const labels = data.map(item => item.date);
        const prices = data.map(item => item.price);

        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stock Prices',
                    data: prices,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    })
    .catch(error => console.error('Error fetching stock data:', error));



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

