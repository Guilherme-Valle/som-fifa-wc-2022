from pyrsistent import b
import scrapy
import pandas
import os

class SelecoesSpider(scrapy.Spider):
    name = "selecoes"
    start_urls = ["https://www.transfermarkt.com/2022-world-cup/teilnehmer/pokalwettbewerb/WM22/"]

    def get_xpath_clubs(self, id_code):
      return '//div[@id="yw' + str(id_code) +'"]//table[@class="items"]//tr//td[@class="zentriert no-border-rechts"]//a'

    def parse(self, response):
        base_url = "https://www.transfermarkt.com"
        XPATH_NATIONAL_TEAMS_ROUND_OF_16 = self.get_xpath_clubs(1)
        XPATH_NATIONAL_TEAMS_ELIMINATED = self.get_xpath_clubs(2)
        print(XPATH_NATIONAL_TEAMS_ROUND_OF_16)
        print(XPATH_NATIONAL_TEAMS_ELIMINATED)

        for national_team_page in response.xpath(XPATH_NATIONAL_TEAMS_ROUND_OF_16):
          link_to_page = national_team_page.xpath('@href').extract()[0]
          url = base_url + link_to_page
          yield scrapy.Request(url=url, callback=self.fetch_national_team_page)

        for national_team_page in response.xpath(XPATH_NATIONAL_TEAMS_ELIMINATED):
          link_to_page = national_team_page.xpath('@href').extract()[0]
          url = base_url + link_to_page
          yield scrapy.Request(url=url, callback=self.fetch_national_team_page)
        
          
    def fetch_national_team_page(self, response):
      XPATH_PLAYERS = '//div[@id="yw1"]//table[@class="items"]//tr'
      
      national_team_name = response.xpath('//title/text()').extract_first()
      national_team_players_names = response.xpath(XPATH_PLAYERS + '//td[@class="hauptlink"]//div//span[@class="hide-for-small"]//a').xpath('@title').extract()
      national_team_players_values = response.xpath(XPATH_PLAYERS + '//td[@class="rechts hauptlink"]//a/text()').extract()
      
      national_team_list = [national_team_name]
      dataframe_columns = ['national_team_name']

      for i in range(len(national_team_players_names)):
        national_team_list.append(national_team_players_names[i])
        dataframe_columns.append('player_' + str(i + 1) + '_name')
        
        national_team_list.append(national_team_players_values[i])
        dataframe_columns.append('player_' + str(i + 1) + '_value')

      dataframe = pandas.DataFrame([national_team_list], columns=dataframe_columns)
      output_path = os.getcwd() + '/national_teams.csv'
      dataframe.to_csv(output_path, mode='a', header=not os.path.exists(output_path),
                             index=False)
