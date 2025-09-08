from configs import *

root_dir = os.path.dirname(__file__)
db_file = os.path.join(root_dir,'database.db')


class Utils:
    @staticmethod
    def load_proxies():
        proxies = []
        file = os.path.join(root_dir,'universals','proxies.txt')
        with open(file,"r") as f:
            for proxy in f.readlines():
                proxy = proxy.replace("\n","").split(":")
                ip = proxy[0]
                port = proxy[1]
                username = proxy[2]
                password = proxy[3] if len(proxy) > 3 else None
                if password is not None:
                    proxy = {
                        "http": f'http://{username}:{password}@{ip}:{port}',
                        "https": f'http://{username}:{password}@{ip}:{port}'
                    }
                else:
                    proxy = {
                        "http": f'http://{username}:@{ip}:{port}',
                        "https": f'http://{username}:@{ip}:{port}'
                    }
                    
                proxies.append(proxy)

        return proxies
    
    @staticmethod
    def get_proxy_cert(proxy_cert):
        return os.path.join(root_dir,proxy_cert)
    
    @staticmethod
    def load_sports():
        file = os.path.join(root_dir,'universals','sports.json')
        with open(file,"r") as f:
            data = json.load(f)
        return data.get('sports', [])
    
    @staticmethod
    def load_bookies():
        file = os.path.join(root_dir,'universals','bookies.json')
        with open(file,"r") as f:
            data = json.load(f)
        return data
    
    @staticmethod
    def load_flash_bookies(country='NG'):
        file = os.path.join(root_dir,'flashscore','bookies.json')
        with open(file,"r") as f:data = json.load(f)
        return [value for key,value in data.items() if key == country]

    @staticmethod
    def generate_android_version():
        major_version = random.randint(2, 10)
        minor_version = random.randint(0, 9)
        build_version = random.randint(0, 9999)
        return f"{major_version}.{minor_version}.{build_version}"
    
    @staticmethod
    def generate_android_device():
        devices = [
                "Samsung Galaxy S21",
                "Samsung Galaxy S6",
                "Samsung Galaxy S5",
                "Samsung Galaxy S7",
                "Samsung Galaxy S8",
                "Samsung Galaxy S8+",
                "Samsung Galaxy S9",
                "Samsung Galaxy S9+",
                "Samsung Galaxy S10",
                "Samsung Galaxy S20",
                "Samsung Galaxy Note8",
                "Samsung Galaxy Note9",
                "Samsung Galaxy Note8+",
                "Samsung Galaxy Note9+",
                "Samsung Galaxy Note10",
                "Samsung Galaxy Note10+",
                "Google Pixel 5",
                "Google Pixel 4",
                "Google Pixel 3",
                "OnePlus 9 Pro",
                "OnePlus 8T",
                "OnePlus 8",
                "Sony Xperia 1 III",
                "Sony Xperia 5 II",
                "Sony Xperia 10 III",
                "Motorola Edge+",
                "Motorola Razr",
                "Xiaomi Mi 11",
                "Xiaomi Mi 10",
                "Xiaomi Redmi Note 10",
                "Nokia 8.3",
                "Nokia 5.4",
                "Huawei Mate 40 Pro",
                "Huawei P40 Pro",
                "LG Wing",
                "LG Velvet",
        ]
        return random.choice(devices)
    
    @staticmethod
    def generate_user_agent(device, count):
        if str(device).lower() == 'android':
            devices = Utils.generate_android_device()
            devices = devices * (count // len(devices)) + devices[:count % len(devices)]
            browsers = [
                {"name":"Chrome","version":f"{random.choice([90,120])}.0.{random.choice([0,4430])}.{random.choice([0,210])}"},
                {"name":"Firefox","version":f"{random.choice([90,121])}.0.{random.choice([0,4430])}.{random.choice([0,210])}"},
            ]
            browser = random.choice(browsers)
            return f"Mozilla/5.0 (Linux; Android {Utils.generate_android_version()}; {Utils.generate_android_device()}) AppleWebKit/537.36 (KHTML, like Gecko) {browser['name']}/{browser['version']} Mobile Safari/537.36"
        else:
            return UserAgent(use_external_data=True)
    
    @staticmethod
    def time_diff(timestamp):
        try:
            time_secs = timestamp / 1000
            datetime_object = datetime.utcfromtimestamp(time_secs)
            current_time = datetime.utcnow()
            return True,current_time > datetime_object

        except Exception as error:
            return False,error


    @staticmethod
    def write_log(message, log_file_path=logs_file):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file_path, 'a',encoding='utf-8') as log_file:
            log_file.write(f"[{current_datetime}] [LOG] {message}\n")

        print(message)

    @staticmethod
    def write_arb(message, log_file_path=arbs_file):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file_path, 'a',encoding='utf-8') as log_file:
            log_file.write(f"[{current_datetime}] [LOG] {message}\n")

        print(message)

    @staticmethod
    def check_values(values:list):
        for value in values:
            if value is None or not value or len(value) < 1:
                return False
        else:return True

    @staticmethod
    def compare_date(timestamp_str,days_ago=7):
        """
        Check if the given ISO 8601 UTC timestamp string is at least 7 days old.
        Returns True or False.
        """
        if not timestamp_str:return False
        try:
            try:
                dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            
            except ValueError: 
                dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")

            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return now - dt_utc <= timedelta(days=days_ago)
        
        except Exception:
            return False
        
    @staticmethod
    def convert_timestamp(value):
        """
        Converts a Unix timestamp to a readable UTC datetime string.
        """
        try:
            return datetime.utcfromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, TypeError):
            return value
        
if __name__ == '__main__':
    print(Utils.compare_date('2025-08-13T08:32:00.630Z'))
    print(Utils.convert_timestamp(1633072800))