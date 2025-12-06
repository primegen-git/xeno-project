import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import CircularProgress from "@mui/material/CircularProgress";
import BasicLayout from "layouts/authentication/components/BasicLayout";
import Card from "@mui/material/Card";

function ShopsCallback() {
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const handleCallback = async () => {
            const queryParams = new URLSearchParams(location.search);
            const code = queryParams.get("code");
            const shop = queryParams.get("shop");
            const state = queryParams.get("state") || "";

            if (code && shop) {
                try {
                    const response = await axios.get(
                        `${process.env.REACT_APP_BACKEND_URL}/shops/callback?code=${code}&shop=${shop}&state=${state}`,
                        { withCredentials: true }
                    );

                    if (response.data.success) {
                        localStorage.setItem("shop_name", shop);
                        window.dispatchEvent(new Event("auth-change"));
                        const isLogin = response.data.is_login;
                        if (isLogin) {
                            // Redirect to PostAuth with is_login=true to trigger auto-fetch
                            navigate("/post-auth?is_login=true");
                        } else {
                            // Redirect to PostAuth with is_login=false to show options
                            navigate("/post-auth?is_login=false");
                        }
                    }
                } catch (error) {
                    console.error("Callback failed", error);
                    alert("Authentication failed. Please try again.");
                    navigate("/authentication/sign-in");
                }
            } else {
                console.error("Missing code or shop param");
                navigate("/authentication/sign-in");
            }
        };

        handleCallback();
    }, [location, navigate]);

    return (
        <BasicLayout>
            <Card>
                <MDBox
                    variant="gradient"
                    bgColor="info"
                    borderRadius="lg"
                    coloredShadow="info"
                    mx={2}
                    mt={-3}
                    p={2}
                    mb={1}
                    textAlign="center"
                >
                    <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
                        Authenticating...
                    </MDTypography>
                </MDBox>
                <MDBox pt={4} pb={3} px={3} textAlign="center">
                    <CircularProgress color="info" />
                </MDBox>
            </Card>
        </BasicLayout>
    );
}

export default ShopsCallback;
