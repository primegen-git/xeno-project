import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";
import SimpleLineChart from "examples/Charts/LineCharts/SimpleLineChart";
import Projects from "layouts/dashboard/components/Projects";
function Dashboard() {
  const { state } = useLocation();
  const [stats, setStats] = useState({
    customers: 0,
    products: 0,
    orders: 0,
  });
  const [salesData, setSalesData] = useState([]);
  const [ordersData, setOrdersData] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);

  const processGraphData = (sales, orders) => {
    const months = [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ];

    const salesArray = new Array(12).fill(0);
    const ordersArray = new Array(12).fill(0);

    if (Array.isArray(sales)) {
      sales.forEach((item) => {
        if (item && item.month) {
          const index = months.indexOf(item.month.trim());
          if (index !== -1) {
            salesArray[index] = item.sales;
          }
        }
      });
    }

    if (Array.isArray(orders)) {
      orders.forEach((item) => {
        if (item && item.month) {
          const index = months.indexOf(item.month.trim());
          if (index !== -1) {
            ordersArray[index] = item.orders;
          }
        }
      });
    }

    setSalesData(salesArray);
    setOrdersData(ordersArray);
  };

  const fetchData = async () => {
    try {
      const [
        customersRes,
        productsRes,
        ordersRes,
        topCustomersRes,
        salesByMonthRes,
        ordersByMonthRes,
      ] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_customers`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_products`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/total_orders`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/top_customers`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/sales_by_month`, {
          withCredentials: true,
        }),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/fetch/orders_by_month`, {
          withCredentials: true,
        }),
      ]);
      setStats({
        customers: customersRes.data,
        products: productsRes.data,
        orders: ordersRes.data,
      });
      setTopCustomers(topCustomersRes.data.data || []);
      processGraphData(salesByMonthRes.data, ordersByMonthRes.data);
    } catch (error) {
      console.error("Error fetching dashboard data", error);
    }
  };

  useEffect(() => {
    if (state?.data) {
      setStats(state.data.stats);
      setTopCustomers(state.data.topCustomers);
      processGraphData(state.data.salesByMonth, state.data.ordersByMonth);
    } else {
      fetchData();
    }
  }, [state]);

  useEffect(() => {
    const eventSource = new EventSource(`${process.env.REACT_APP_BACKEND_URL}/events`, {
      withCredentials: true,
    });

    eventSource.onmessage = (event) => {
      const message = event.data;
      if (message === "customer_created") {
        setStats((prev) => ({ ...prev, customers: prev.customers + 1 }));
      } else if (message === "product_created") {
        setStats((prev) => ({ ...prev, products: prev.products + 1 }));
      } else if (message === "order_created") {
        fetchData();
      }
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const ordersChartData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
      {
        label: "Orders",
        color: "info",
        data: ordersData,
      },
    ],
  };

  const revenueChartData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
      {
        label: "Revenue",
        color: "success",
        data: salesData,
      },
    ],
  };
  return (
    <DashboardLayout>
      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="people"
                title="Total Customers"
                count={stats.customers}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="inventory_2"
                title="Total Products"
                count={stats.products}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="shopping_cart"
                title="Total Orders"
                count={stats.orders}
                percentage={{ color: "success", amount: "", label: "Updated just now" }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <MDBox mb={3}>
                <SimpleLineChart
                  color="info"
                  title="Orders"
                  description="Last 12 Months"
                  chart={ordersChartData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6}>
              <MDBox mb={3}>
                <SimpleLineChart
                  color="success"
                  title="Revenue"
                  description="Last 12 Months"
                  chart={revenueChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Projects topCustomers={topCustomers} />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
    </DashboardLayout>
  );
}
export default Dashboard;
