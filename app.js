const fs = require("fs")
const path = require("path")
const crypto = require("crypto")
const request = require("request")
const { Builder, By, Key, until } = require("selenium-webdriver")
const chrome = require("selenium-webdriver/chrome")
const proxy = require("selenium-webdriver/proxy")
const proxyChain = require("proxy-chain")
require('console-stamp')(console, {
  format: ':date(yyyy/mm/dd HH:MM:ss.l)'
})

// 加载环境变量
require("dotenv").config()

// 设置 ChromeDriver
require("chromedriver")

const CRX_URL = "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=98.0.4758.102&acceptformat=crx2,crx3&x=id%3D${extensionId}%26uc&nacl_arch=x86-64"
const USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"

const extensionId = "caacbgbklghmpodbdafajbgdnegacfmo"
const USER = process.env.APP_USER || ""
const PASSWORD = process.env.APP_PASS || ""
const ALLOW_DEBUG = !!process.env.DEBUG?.length || false
const EXTENSION_FILENAME = "app.crx"
const PROXY = process.env.PROXY || undefined

// 添加启动横幅
console.log("\n")
console.log("========================================================")
console.log("                Gradient Network Bot")
console.log("--------------------------------------------------------")
console.log("  开发者: 小林 (@yoyomyoyoa)")
console.log("--------------------------------------------------------")
console.log("  免责声明:")
console.log("  1. 本项目仅供学习交流使用")
console.log("  2. 使用本项目产生的任何后果由使用者自行承担")
console.log("  3. 请遵守相关法律法规，不要滥用")
console.log("========================================================")
console.log("\n")

console.log("-> 程序启动中...")
console.log("-> 账号:", USER)
console.log("-> 密码:", PASSWORD)
console.log("-> 代理:", PROXY)
console.log("-> 调试模式:", ALLOW_DEBUG ? "开启" : "关闭")

if (!USER || !PASSWORD) {
  console.error("请设置环境变量 APP_USER 和 APP_PASS")
  process.exit(1)
}

if (ALLOW_DEBUG) {
  console.log(
    "-> 调试模式已开启！将在出错时生成截图和控制台日志！"
  )
}

async function downloadExtension(extensionId) {
  const url = CRX_URL.replace("${extensionId}", extensionId)
  const headers = { "User-Agent": USER_AGENT }

  console.log("-> 正在下载扩展，地址:", url)

  if (fs.existsSync(EXTENSION_FILENAME) && fs.statSync(EXTENSION_FILENAME).mtime > Date.now() - 86400000) {
    console.log("-> 扩展已存在！跳过下载...")
    return
  }

  return new Promise((resolve, reject) => {
    request({ url, headers, encoding: null }, (error, response, body) => {
      if (error) {
        console.error("-> 下载扩展时出错:", error)
        return reject(error)
      }
      if (response.statusCode !== 200) {
        console.error("-> 下载扩展失败！状态码:", response.statusCode)
        return reject(new Error(`下载扩展失败！状态码: ${response.statusCode}`))
      }
      fs.writeFileSync(EXTENSION_FILENAME, body)
      if (ALLOW_DEBUG) {
        const md5 = crypto.createHash("md5").update(body).digest("hex")
        console.log("-> 扩展 MD5:", md5)
      }
      console.log("-> 扩展下载成功！")
      resolve()
    })
  })
}

async function takeScreenshot(driver, filename) {
  // if ALLOW_DEBUG is set, taking screenshot
  if (!ALLOW_DEBUG) {
    return
  }

  const data = await driver.takeScreenshot()
  fs.writeFileSync(filename, Buffer.from(data, "base64"))
}

async function generateErrorReport(driver) {
  //write dom
  const dom = await driver.findElement(By.css("html")).getAttribute("outerHTML")
  fs.writeFileSync("error.html", dom)

  await takeScreenshot(driver, "error.png")

  const logs = await driver.manage().logs().get("browser")
  fs.writeFileSync(
    "error.log",
    logs.map((log) => `${log.level.name}: ${log.message}`).join("\n")
  )
}

// 检查 Chrome 路径
const CHROME_PATHS = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  process.env.CHROME_PATH
].filter(Boolean)

async function findChromePath() {
  for (const path of CHROME_PATHS) {
    if (fs.existsSync(path)) {
      console.log("-> Chrome 路径:", path)
      return path
    }
  }
  throw new Error("未找到 Chrome 浏览器！请安装 Chrome 浏览器或设置 CHROME_PATH 环境变量。")
}

async function startBrowser() {
  console.log("-> 正在启动浏览器...")
  console.log("-> 浏览器启动配置:")
  console.log("   - 无头模式: 开启")
  console.log("   - 窗口大小: 1920x1080")
  console.log("   - 禁用GPU: 是")
  console.log("   - 禁用扩展: 否")

  const chromePath = await findChromePath()
  
  const options = new chrome.Options()
    .setChromeBinaryPath(chromePath)
    .addArguments('--headless=new')
    .addArguments('--no-sandbox')
    .addArguments('--disable-dev-shm-usage')
    .addArguments('--disable-gpu')
    .addArguments('--window-size=1920,1080')
    .addArguments(`--user-agent=${USER_AGENT}`)

  if (PROXY) {
    console.log("-> 正在设置代理...", PROXY)
    const newProxyUrl = await proxyChain.anonymizeProxy(PROXY)
    console.log("-> 新代理地址:", newProxyUrl)
    const proxyUrl = new URL(newProxyUrl)
    console.log("-> 代理主机:", proxyUrl.hostname)
    console.log("-> 代理端口:", proxyUrl.port)
    options.addArguments(`--proxy-server=socks5://${proxyUrl.hostname}:${proxyUrl.port}`)
    console.log("-> 代理设置完成！")
  } else {
    console.log("-> 未设置代理！")
  }

  // 添加扩展
  options.addExtensions(path.resolve(__dirname, EXTENSION_FILENAME))
  console.log("-> 扩展已添加！", EXTENSION_FILENAME)

  try {
    const driver = await new Builder()
      .forBrowser('chrome')
      .setChromeOptions(options)
      .build()

    console.log("-> 浏览器启动成功！")
    return driver
  } catch (error) {
    console.error("-> 浏览器启动失败！错误信息:", error.message)
    throw error
  }
}

async function getProxyIpInfo(driver, proxyUrl) {
  // const url = "https://httpbin.org/ip"
  const url = "https://myip.ipip.net"

  console.log("-> Getting proxy IP info:", proxyUrl)

  try {
    await driver.get(url)
    await driver.wait(until.elementLocated(By.css("body")), 30000)
    const pageText = await driver.findElement(By.css("body")).getText()
    console.log("-> Proxy IP info:", pageText)
  } catch (error) {
    console.error("-> Failed to get proxy IP info:", error)
    throw new Error("Failed to get proxy IP info!")
  }
}

// 主程序
(async function main() {
  try {
    // 先下载扩展
    await downloadExtension(extensionId)
    
    // 启动浏览器
    const driver = await startBrowser()
    
    console.log("-> 正在访问 Gradient Network...")
    await driver.get("https://app.gradient.network/")
    console.log("-> 页面加载成功！")

    const emailInput = By.css('[placeholder="Enter Email"]')
    const passwordInput = By.css('[type="password"]')
    const loginButton = By.css("button")

    await driver.wait(until.elementLocated(emailInput), 30000)
    await driver.wait(until.elementLocated(passwordInput), 30000)
    await driver.wait(until.elementLocated(loginButton), 30000)

    await driver.findElement(emailInput).sendKeys(USER)
    await driver.findElement(passwordInput).sendKeys(PASSWORD)
    await driver.findElement(loginButton).click()

    // wait until find <a href="/dashboard/setting">
    await driver.wait(until.elementLocated(By.css('a[href="/dashboard/setting"]')), 30000)

    console.log("-> Logged in! Waiting for open extension...")

    // 截图登录状态
    takeScreenshot(driver, "logined.png")

    await driver.get(`chrome-extension://${extensionId}/popup.html`)

    console.log("-> Extension opened!")

    // 直到找到 "Status" 文本的 div 元素
    await driver.wait(
      until.elementLocated(By.xpath('//div[contains(text(), "Status")]')),
      30000
    )

    console.log("-> Extension loaded!")

    // if there is a page with a button "I got it", click it
    try {
      const gotItButton = await driver.findElement(
        By.xpath('//button[contains(text(), "I got it")]')
      )
      await gotItButton.click()
      console.log('-> "I got it" button clicked!')
    } catch (error) {
      // save rendered dom to file
      const dom = await driver
        .findElement(By.css("html"))
        .getAttribute("outerHTML")
      fs.writeFileSync("dom.html", dom)
      console.error('-> No "I got it" button found!(skip)')
    }

    // if found a div include text "Sorry, Gradient is not yet available in your region. ", then exit
    try {
      const notAvailable = await driver.findElement(
        By.xpath(
          '//*[contains(text(), "Sorry, Gradient is not yet available in your region.")]'
        )
      )
      console.log("-> Sorry, Gradient is not yet available in your region. ")
      await driver.quit()
      process.exit(1)
    } catch (error) {
      console.log("-> Gradient is available in your region. ")
    }

    // <div class="absolute mt-3 right-0 z-10">
    const supportStatus = await driver
      .findElement(By.css(".absolute.mt-3.right-0.z-10"))
      .getText()


    if (ALLOW_DEBUG) {
      const dom = await driver
        .findElement(By.css("html"))
        .getAttribute("outerHTML")
      fs.writeFileSync("dom.html", dom)
      await takeScreenshot(driver, "status.png")
    }

    console.log("-> Status:", supportStatus)

    if (supportStatus.includes("Disconnected")) {
      console.log(
        "-> Failed to connect! Please check the following: ",
      )
      console.log(`
    - Make sure the proxy is working, by 'curl -vv -x ${PROXY} https://myip.ipip.net'
    - Make sure the docker image is up to date, by 'docker pull overtrue/gradient-bot' and re-start the container.
    - The official service itself is not very stable. So it is normal to see abnormal situations. Just wait patiently and it will restart automatically.
    - If you are using a free proxy, it may be banned by the official service. Please try another static Static Residential proxy.
  `)
      await generateErrorReport(driver)
      await driver.quit()
      setTimeout(() => {
        process.exit(1)
      }, 5000)
    }

    console.log("-> Connected! Starting rolling...")

    // 截图链接状态
    takeScreenshot(driver, "connected.png")

    console.log({
      support_status: supportStatus,
    })

    console.log("-> Lunched!")

    // keep the process running
    setInterval(() => {
      driver.getTitle().then((title) => {
        console.log(`-> [${USER}] Running...`, title)
      })

      if (PROXY) {
        console.log(`-> [${USER}] Running with proxy ${PROXY}...`)
      } else {
        console.log(`-> [${USER}] Running without proxy...`)
      }
    }, 30000)
  } catch (error) {
    console.error("-> 发生错误:", error.message)
    if (ALLOW_DEBUG) {
      console.log("-> 正在保存错误截图...")
      try {
        if (driver) {
          const screenshot = await driver.takeScreenshot()
          const filename = `error_${Date.now()}.png`
          fs.writeFileSync(filename, screenshot, 'base64')
          console.log(`-> 错误截图已保存: ${filename}`)
        }
      } catch (screenshotError) {
        console.error("-> 无法保存错误截图:", screenshotError.message)
      }
    }
    process.exit(1)
  }
})()
