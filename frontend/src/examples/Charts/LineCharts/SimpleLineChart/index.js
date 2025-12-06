import { useMemo } from "react";
import PropTypes from "prop-types";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import configs from "examples/Charts/LineCharts/SimpleLineChart/configs";
import colors from "assets/theme/base/colors";
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);
function SimpleLineChart({ color, title, description, date, chart }) {
  const chartDatasets = chart.datasets
    ? chart.datasets.map((dataset) => ({
        ...dataset,
        tension: 0,
        pointRadius: 5,
        pointBorderColor: "transparent",
        pointBackgroundColor: colors[color] ? colors[color].main : colors.dark.main,
        borderColor: colors[color] ? colors[color].main : colors.dark.main,
        borderWidth: 4,
        backgroundColor: "transparent",
        fill: true,
        maxBarThickness: 6,
      }))
    : [];
  const { data, options } = configs(chart.labels || [], chartDatasets);
  const renderChart = (
    <MDBox py={2} pr={2} pl={2}>
      {title || description ? (
        <MDBox display="flex" px={description ? 1 : 0} pt={description ? 1 : 0}>
          <MDBox mt={0}>
            {title && <MDTypography variant="h6">{title}</MDTypography>}
            <MDBox mb={2}>
              <MDTypography component="div" variant="button" color="text">
                {description}
              </MDTypography>
            </MDBox>
          </MDBox>
        </MDBox>
      ) : null}
      {useMemo(
        () => (
          <MDBox height="12.5rem">
            <Line data={data} options={options} redraw />
          </MDBox>
        ),
        [chart, color]
      )}
    </MDBox>
  );
  return title || description ? <Card>{renderChart}</Card> : renderChart;
}
SimpleLineChart.defaultProps = {
  color: "info",
  description: "",
};
SimpleLineChart.propTypes = {
  color: PropTypes.oneOf(["primary", "secondary", "info", "success", "warning", "error", "dark"]),
  title: PropTypes.string.isRequired,
  description: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  date: PropTypes.string,
  chart: PropTypes.objectOf(PropTypes.array).isRequired,
};
export default SimpleLineChart;
