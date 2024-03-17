from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
import pandas as pd
import time

# calculates the implied probability of the odds. Example: if there is yes and no outcome.
# Yes being - 1.5 and No - 2.0 then the calculation would be (1/1.5) + (1/2.0).
# If Implied_Prob is more than 100% its in the broker's favour if its in less than 100% its in the better's favour.
def Calculate_Implied_Prob(list):
    result = 0.0
    for num in list:
        result += (1/num)
    return result*100

# turn the filter list into a Select object
def Get_Bet_Type_Select_Object():
    List_of_Bet_Type_driver = driver.find_element(By.XPATH, "//div[@id='tabs-upcomingFootball']//select[@name='upcomingFootball_filterBetType']")
    print(List_of_Bet_Type_driver)
    select_List_of_Bet_Type_driver = Select(List_of_Bet_Type_driver)
    return select_List_of_Bet_Type_driver

# Extract information from 1x2 filter page
def Extract_1x2_BetType():
    df = pd.DataFrame(columns = ["id","Event","Date","Time","Home_odds","Draw_odds","Away_odds","Implied_Prob"])
    Event_list_groups = driver.find_elements(By.XPATH,"//div[@id='tabs-upcomingFootball']//div[@class='event-list__group']")
    for Event_list in Event_list_groups:
        Event_Date = Event_list.find_element(By.CLASS_NAME,"event-list__group-title").text.split(",")[1].strip()
        Match_Rows = Event_list.find_elements(By.XPATH,"div/table/tbody/tr")
        for Match_Row in Match_Rows:
            # Extract values from the browser - Start #
            Match_Time = Match_Row.find_element(By.CLASS_NAME,"event-list__event-start-time").text.strip()
            Match_id = int(Match_Row.find_element(By.CLASS_NAME,"text-center").text.strip())
            Match_name = Match_Row.find_element(By.CLASS_NAME,"event-list__event-name").text.strip()
            Match_Odds = []
            for odds in Match_Row.find_elements(By.CLASS_NAME, "button-outcome__price"):
                try:
                    odd_value = float(odds.text.strip())
                except ValueError:
                    odd_value = None
                Match_Odds.append(odd_value)
            # Extract values from the browser - End #
                
            # Put Extracted Values into a pandas dataframe - Start #
            index = len(df)
            df.loc[index] = (Match_id,Match_name,Event_Date,Match_Time,Match_Odds[0],Match_Odds[1],Match_Odds[2],"" if (None in Match_Odds) else Calculate_Implied_Prob(Match_Odds))
            # Put Extracted Values into a pandas dataframe - End #

    # export pandas dataframe as a csv #
    df.to_csv("one_slash_two.csv",index=False)

# Extract information from Will_Both_Teams_Score filter page
def Extract_Will_Both_Teams_Score():
    df_Will_Both_Teams_Score = pd.DataFrame(columns = ["id","Event","Date","Time","Yes_Odds","No_Odds","Implied_Prob"])
    Event_list_groups = driver.find_elements(By.XPATH,"//div[@id='tabs-upcomingFootball']//div[@class='event-list__group']")
    for Event_list in Event_list_groups:
        Event_Date = Event_list.find_element(By.CLASS_NAME,"event-list__group-title").text.split(",")[1].strip()
        Match_Rows = Event_list.find_elements(By.CLASS_NAME,"event-list__event")
        for Match_Row in Match_Rows:

            # Extract values from the browser - Start #
            Match_Time = Match_Row.find_element(By.CLASS_NAME,"event-list__event-start-time").text.strip()
            Match_id = int(Match_Row.find_element(By.CLASS_NAME,"event-list__event-retail-id").text.strip())
            Match_name = Match_Row.find_element(By.CLASS_NAME,"event-list__event-name").text.strip()
            Match_Odds = [float(odds.text.strip()) for odds in Match_Row.find_elements(By.CLASS_NAME,"button-outcome__price")]
            # Extract values from the browser - End #

            # Put Extracted Values into a pandas dataframe - Start #
            df_Will_Both_Teams_Score_index = len(df_Will_Both_Teams_Score)
            df_Will_Both_Teams_Score.loc[df_Will_Both_Teams_Score_index] = (Match_id,Match_name,Event_Date,Match_Time,Match_Odds[0],Match_Odds[1],Calculate_Implied_Prob(Match_Odds))
            # Put Extracted Values into a pandas dataframe - End #

    df_Will_Both_Teams_Score.to_csv("Will_Both_Teams_Score.csv",index=False)

def main()->None:
    # load the browser and direct to the url
    global service
    global driver
    service = Service(executable_path = "chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.get("https://online.singaporepools.com/en/sports")

    # wait until the Signapore Pools logo is loaded
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.b-header__logo.navbar-btn.pull-left"))
    )

    # wait for page to load for 3 seconds
    time.sleep(3)

    select_List_of_Bet_Types = Get_Bet_Type_Select_Object()
    Display_button = driver.find_element(By.XPATH, "//div[@id='tabs-upcomingFootball']//button[@type='button']")
    List_Filter_Go_Through = ["1X2","Will Both Teams Score"] # the list of Filters will web scrape through

    for Bet_Type_Chosen in List_Filter_Go_Through:
        # select the filter to display the bets
        select_List_of_Bet_Types.select_by_visible_text(Bet_Type_Chosen)
        Display_button.click()

        # wait for the page to load
        time.sleep(4)

        # Press the Load More button until all the data is loaded
        while True:
            try:
                # search for load more button and if there is a Load_more_button_continue
                Load_more_button = driver.find_element(By.LINK_TEXT,"LOAD ALL EVENTS")
                Load_more_button.click()
            except NoSuchElementException:
                # once all the bets are loaded. exit the while loop
                break
        
        # web scrape and export the information as csv
        if Bet_Type_Chosen == "1X2":
            Extract_1x2_BetType()
        
        if Bet_Type_Chosen == "Will Both Teams Score":
            Extract_Will_Both_Teams_Score()
    
    driver.quit()

if __name__ == "__main__":
    main()

