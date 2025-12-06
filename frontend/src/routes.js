import Dashboard from "layouts/dashboard";
import FilterByDate from "layouts/filter-by-date";
import SignIn from "layouts/authentication/sign-in";
import SignUp from "layouts/authentication/sign-up";
import PostAuth from "layouts/post-auth";
import Icon from "@mui/material/Icon";
const routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
  },
  {
    type: "collapse",
    name: "Filter by Date",
    key: "filter-by-date",
    icon: <Icon fontSize="small">date_range</Icon>,
    route: "/filter-by-date",
    component: <FilterByDate />,
  },
  {
    type: "collapse",
    name: "Sign In",
    key: "sign-in",
    icon: <Icon fontSize="small">login</Icon>,
    route: "/authentication/sign-in",
    component: <SignIn />,
  },
  {
    type: "collapse",
    name: "Sign Up",
    key: "sign-up",
    icon: <Icon fontSize="small">assignment</Icon>,
    route: "/authentication/sign-up",
    component: <SignUp />,
  },
  {
    type: "collapse",
    name: "Post Auth",
    key: "post-auth",
    icon: <Icon fontSize="small">assignment</Icon>,
    route: "/post-auth",
    component: <PostAuth />,
  },
];
export default routes;
