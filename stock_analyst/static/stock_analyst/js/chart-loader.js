
let currentChart = null;
let stockData = null; // Global variable to store fetched data

// Function to fetch and store data
async function fetchStockData() {
  if (stockData) {
    return stockData; // Return cached data if already fetched
  }
  
  try {
    const response = await fetch('/main/data_stream');
    stockData = await response.json();
    return stockData;
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
}

function destroyCurrentChart() {
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }
}

function disableActiveButton(active) {
  const activeButton = document.getElementById(active);
  activeButton.classList.add('active')
  const high = document.getElementById('high_button');
  if (activeButton !== high) {
    high.classList.remove('active');
  }
  const low = document.getElementById('low_button');
  if (activeButton !== low) {
    low.classList.remove('active');
  }
  const open = document.getElementById('open_button');
  if (activeButton !== open) {
    open.classList.remove('active');
  }
  const close =  document.getElementById('close_button');
  if (activeButton !== close) {
    close.classList.remove('active');
  }
  const volume = document.getElementById('volume_button');
  if (activeButton !== volume) {
    volume.classList.remove('active');
  }
}

async function loadHighsChart() {
  destroyCurrentChart();

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const highs = companies.map(company => company.high);
    const date = companies.map(company => company.date);

    currentChart = new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
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
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock High Prices by Company'
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Price ($)' }
            },
            x: {
              title: { display: true, text: 'Company' }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading highs data:', error);
  }
  disableActiveButton('high_button');
}

async function loadLowsChart() {
  destroyCurrentChart();

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const lows = companies.map(company => company.low);
    const date = companies.map(company => company.date);

    currentChart = new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Stock Low Prices ($)',
            data: lows,
            backgroundColor: [
              'rgba(255, 99, 132, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 205, 86, 0.8)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 205, 86, 1)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock Low Prices by Company'
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Price ($)' }
            },
            x: {
              title: { display: true, text: 'Company' }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading lows data:', error);
  }
  disableActiveButton('low_button');
}

async function loadOpenChart() {
  destroyCurrentChart();

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const open = companies.map(company => company.open);
    const date = companies.map(company => company.date);

    currentChart = new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Stock Opening Prices ($)',
            data: open,
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
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock Opening Prices by Company'
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Price ($)' }
            },
            x: {
              title: { display: true, text: 'Company' }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading opening data:', error);
  }
  disableActiveButton('open_button');
}

async function loadCloseChart() {
  destroyCurrentChart();

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const close = companies.map(company => company.close);
    const date = companies.map(company => company.date);

    currentChart = new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Stock Closing Prices ($)',
            data: close,
            backgroundColor: [
              'rgba(255, 205, 86, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 99, 132, 0.8)'
            ],
            borderColor: [
              'rgba(255, 205, 86, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock Closing Prices by Company'
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Price ($)' }
            },
            x: {
              title: { display: true, text: 'Company' }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading closing data:', error);
  }
  disableActiveButton('close_button');
}

async function loadVolumeChart() {
  destroyCurrentChart();

  try {
    const data = await fetchStockData();
    const companies = Object.values(data);
    const labels = companies.map(company => company.company_name);
    const volume = companies.map(company => company.volume);
    const date = companies.map(company => company.date);

    currentChart = new Chart(
      document.getElementById('main_highs'),
      {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Volume for Day (ea.)',
            data: volume,
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
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Stock Volume Movement by Company'
            },
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: function(context) {
                  const companyIndex = context.dataIndex;
                  return 'Date: ' + date[companyIndex];
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Units (ea.)' }
            },
            x: {
              title: { display: true, text: 'Company' }
            }
          }
        }
      }
    );
  } catch (error) {
    console.error('Error loading volume data:', error);
  }
  disableActiveButton('volume_button');
}

// Load the default chart on page load
document.addEventListener('DOMContentLoaded', function() {
  loadHighsChart();
});
