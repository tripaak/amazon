# v0.1

1. Tool is based on selenium as python requests are blocked by amazon.com bot detection.
2. this tools works in on headless mode as headless is blocked by amazon
3. In order to use this tool user has to disbale "Two-Step Verification (2SV) Settings"


# v0.2
1. 2FA login handelling with timeout period of 3 minutes 
2. If user is already login skip the auth part and navigate to orders page
3. If Generic page is displayed by Amazon , navigate to "https://www.amazon.com/gp/css/homepage.html"