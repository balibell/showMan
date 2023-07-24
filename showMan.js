const path = require("path");
const fs = require("fs");
const sharp = require("sharp");
const log4js = require('log4js')
const fse = require('fs-extra');

log4js.configure({
  appenders: {
    file: {
      type: 'file',
      filename: 'app.log',
      layout: {
        type: 'pattern',
        pattern: '%r %p - %m',
      }
    }
  },
  categories: {
    default: {
      appenders: ['file'],
      level: 'debug'
    }
  }
})
const logger = log4js.getLogger()
const DEBUG = false
const TMP_DIR = path.join(__dirname, 'tmp', nowTimeStr())


const args = process.argv.slice();
args.splice(0, 2);

const trimParamStr = args[0]
const doTrim = !!trimParamStr;
const trimParamArr = doTrim ? JSON.parse(trimParamStr) : []
let readFilePath = args[1];
let localImageDirectory = args[2];
const useLocalImage = !!parseInt(args[3]);
const splitNum = parseInt(args[4]) || 1;
const targetFilePathPrefix = args[5];
const useModifyTime = !!parseInt(args[6]);

console.log(`doTrim: ${doTrim}`)
console.log(`trimParamStr: ${trimParamStr}`)
console.log(`useLocalImage: ${useLocalImage}`)
console.log(`useModifyTime: ${useModifyTime}`)


const cofirmDeleteFilePath = './confirmDelete.json';
const confirmEditMapFilePath = './confirmEditMap.json';
const confirmCroppedFilePath = './confirmCropped.txt';
const templateFilePath = 'template.html';
const TXT_SUFFIX = '.txt'
const PNG_SUFFIX = '.png'
const JPEG_SUFFIX = '.jpeg'
const JPG_SUFFIX = '.jpg'
const PROPMTS_ARR = 'prompts_arr'
const CROP_ARR_1 = 'crop_arr_1'
const CROP_ARR_2 = 'crop_arr_2'


// trimUseMap
let itemFullArr = []
const trimUseMap = {}

const MAX_RES = 4096*4096
const KEY_MIN_RES = 'minRes'
const KEY_MIN_WH_RATIO = 'minWHRatio'
const KEY_MAX_WH_RATIO = 'maxWHRatio'
let trimFilterParams = {}

if (doTrim && trimParamArr.length >= 4) {
  trimFilterParams[KEY_MIN_RES] = trimParamArr[0] * trimParamArr[1]
  trimFilterParams[KEY_MIN_WH_RATIO] = trimParamArr[2]
  trimFilterParams[KEY_MAX_WH_RATIO] = trimParamArr[3]

  console.log(`trimFilterParams:`)
  console.log(trimFilterParams)
} else {
  trimFilterParams[KEY_MIN_RES] = 512*512
  trimFilterParams[KEY_MIN_WH_RATIO] = 0.3
  trimFilterParams[KEY_MAX_WH_RATIO] = 1.32
}


// 已屏蔽的图片
let confirmDeleteModelIds = [];
try {
  confirmDeleteModelIds = JSON.parse(fs.readFileSync(cofirmDeleteFilePath, 'utf8'))
} catch (e) {}

// 有裁剪的图片
let confirmCroppedList = [];
try {
  confirmCroppedList = fs.readFileSync(confirmCroppedFilePath, 'utf8').split('\n')
  confirmCroppedList = confirmCroppedList.filter((item) => item.trim() !== '');
} catch (e) {}


// 修改过的图片
let confirmEditMap = {}
try {
  confirmEditMap = JSON.parse(fs.readFileSync(confirmEditMapFilePath, 'utf8'));
} catch (e) {}

function fileNameToUrl(name, fileName) {
  return `https://c-ssl.dtstatic.com/uploads/${name}/${fileName.substr(0, 6)}/${fileName.substr(6, 2)}/${fileName}`
}

async function readImageSizeAndModiyTime(imagePath) {
  return new Promise(function (resolve, reject) {

    sharp(imagePath)
    .metadata()
    .then(metadata => {
      // 输出图片尺寸

      if (useModifyTime) {
        fs.stat(imagePath, (err, stats) => {
          if (err) {
            resolve({'width': metadata.width, 'height': metadata.height})
            return;
          }
        
          // 获取文件的修改时间
          const mtime = stats.mtime.getTime();
          console.log('文件修改时间:', mtime);
          resolve({'width': metadata.width, 'height': metadata.height, 'mtime': mtime})
        });
      } else {
        resolve({'width': metadata.width, 'height': metadata.height})
      }
    })
    .catch(err => {
      error('读取图片尺寸时发生错误:', err);
      reject(err)
    });
  });
}

async function filterItem(item, dirPath) {
  let fileName = item.file_name
  let imageFilePath = path.join(localImageDirectory, fileName)
  try {
    fs.accessSync(imageFilePath, fs.constants.F_OK);

    let shouldMoveReason = ''

    if (confirmDeleteModelIds.indexOf(fileName) > -1) {
      // log(`is deleteddddddddd`)
      shouldMoveReason = 'to be delete'
    } else if (!isNormalImage(imageFilePath)) {
      shouldMoveReason = 'not allowed image'
    }


    if (!shouldMoveReason) {
      let imageSize = await readImageSizeAndModiyTime(imageFilePath)
      if (!filterMatched(imageSize)) {
        shouldMoveReason = `size not match width: ${imageSize.width} height: ${imageSize.height}`
      } else {
        item.image_url1 = fileNameToUrl('item', fileName)
        item.image_url2 = fileNameToUrl('blog', fileName)
        item.image_width = imageSize.width
        item.image_height = imageSize.height
        item.mtime = imageSize.mtime || 0
        // log('image width:'+ item.image_width + ' height:' + item.image_height)
        
        // 优先使用 map 里的数据
        let prompts_arr = []
        let confirmItem = confirmEditMap[fileName]
        if (confirmItem && confirmItem[PROPMTS_ARR]) {
          prompts_arr = confirmItem[PROPMTS_ARR]
          item[CROP_ARR_1] = confirmItem[CROP_ARR_1]
          item[CROP_ARR_2] = confirmItem[CROP_ARR_2]
        } else if (confirmItem && !confirmItem[PROPMTS_ARR]) {
          // edit文件里只有crop信息，缺少prompts
          logger.warn(`prompts not found in edit info file file_name is: ${fileName}`)
        }
      
      
      
      
        if (!prompts_arr.length) {
          // 先看看如果设定参数优先
          if (item.prompts_arr && item.prompts_arr.length) {
            prompts_arr = item.prompts_arr
          } else {
            for (let key in item.prompts) {
              prompts_arr.push(key)
            }
          }
        }
        
        item.prompts_arr = prompts_arr
        item.img_dir = `${dirPath}`
        return item
      }
    }


    if (doTrim && !!shouldMoveReason) {
      delete trimUseMap[fileName]
      moveToTmpSync(imageFilePath, `nouse`, shouldMoveReason)
    }

  } catch (err) {
    // error('image 文件不存在：', err);
    return null;
  }
}

function moveFileSync(sourcePath, destinationPath) {
  if (fs.existsSync(sourcePath)) {
    const destinationDir = path.dirname(destinationPath);

    if (!fs.existsSync(destinationDir)) {
      fs.mkdirSync(destinationDir, { recursive: true });
    }

    fs.renameSync(sourcePath, destinationPath);
  }
}


function doCropImage(sourceFilePath, destFilePath, cropArr) {
  try {
    let tmpDestFilePath = destFilePath
    let needRename = false

    if (path.resolve(tmpDestFilePath) === path.resolve(sourceFilePath)) {
      // 如果 source 和 dest 文件相同
      tmpDestFilePath = `${tmpDestFilePath}_tmp`
      needRename = true
    }

    log(`crop destFilePath ${destFilePath}`)

    sharp(sourceFilePath)
    .extract({ left: cropArr[0], top: cropArr[1], width: cropArr[2], height: cropArr[3] })
    .toFile(tmpDestFilePath, (err) => {
      if (err) {
        error(`crop image error1: ${err}`);
      }

      if (needRename) {
        try {
          fs.renameSync(tmpDestFilePath, sourceFilePath);
        } catch (err) {
          error(`crop image rename error3: ${err}`);
        }
      }
    });
  } catch (err) {
    error(`crop image error2: ${err}`);
  }
}

function filterMatched(imageSize) {
  const width = imageSize.width;
  const height = imageSize.height;
  if (height > 0) {
    const whRatio = width / height
    const res = width * height

    if (whRatio < trimFilterParams[KEY_MIN_WH_RATIO] || whRatio > trimFilterParams[KEY_MAX_WH_RATIO]) {
      return false
    } else if (res < trimFilterParams[KEY_MIN_WH_RATIO] || res > MAX_RES) {
      return false
    }
  }

  return true
}

function isNormalImage(filePath) {
  let lowPath = filePath.toLowerCase()
  return lowPath.endsWith(PNG_SUFFIX) || lowPath.endsWith(JPEG_SUFFIX) || lowPath.endsWith(JPG_SUFFIX) 
}

function genItemId(directoryPath, fileName) {
  let relativePath = path.relative(localImageDirectory, directoryPath)
  let itemId = fileName
  if (relativePath) {
    itemId = `${relativePath}/${itemId}`
  }
  return itemId
}

function genItemIdByFilePath(filePath) {
  let directoryPath = path.dirname(filePath);
  let fileName = path.basename(filePath);
  return genItemId(directoryPath, fileName)
}

function saveCropped(filePath) {
  let itemId = genItemIdByFilePath(filePath)
  if (confirmCroppedList.indexOf(itemId) == -1) {
    confirmCroppedList.push(itemId)
  }
}

async function traverseDirectorySyncAndDoTrim(directoryPath, num=0) {
  const folderName = path.basename(directoryPath);
  const files = fs.readdirSync(path.resolve(directoryPath));


  log(`folder is ${directoryPath}`)

  for (let file of files) {
    const filePath = path.join(directoryPath, file);

    let stats
    try {
      stats = fs.statSync(filePath);
    } catch (err) {
      // error(`doTrim Error loop file: ${filePath}`, err);
      continue
    }

    if (stats.isDirectory()) {
      // Recursively traverse subdirectory
      await traverseDirectorySyncAndDoTrim(filePath, num++);
    } else {
      let fileName = path.basename(filePath);
      let fileExtension = path.extname(filePath);
      let fileNameNoExt = path.basename(filePath, fileExtension);
      let isAllowImage = isNormalImage(fileName)
      // Handle file 不能是 txt 文件
      if (isAllowImage && !fileNameNoExt.endsWith('_cropped')) {
        let fileNameTxt = `${fileNameNoExt}${TXT_SUFFIX}`
        let txtFilePath = path.join(directoryPath, fileNameTxt)
        let imageSize = await readImageSizeAndModiyTime(filePath)
        let isFilterMatched = filterMatched(imageSize);

        let itemId = genItemId(directoryPath, fileName)
        // let itemId = genItemIdByFilePath(path.join(directoryPath, fileName))
        // log('traver itemId: ' + itemId)
        let item = trimUseMap[itemId];
        if (item && isFilterMatched) {
          // 如果 map 里包含这个图片，则生成 prompt txt 文件
  
          // 生成 prompt 文件
          let prompt = item.prompts_arr.join(', ')
          try {
            fs.writeFileSync(txtFilePath, prompt);
            // log('doTrim write prompt txt file ok.')
          } catch (err) {
            error('doTrim Error write file:', err);
          }

          // crop1 & crop2 优先使用 crop1
          let cropdo = item[CROP_ARR_1] || item[CROP_ARR_2]
          if (cropdo) {
            // crop1 会替换原图
            const width = imageSize.width;
            const height = imageSize.height;
            if (width != cropdo[2] || height != cropdo[3]) {
              // 防止反复裁剪
              log(`do crop origin size[${width},${height}] to crop size[${cropdo[2]},${cropdo[3]}]`)
              doCropImage(filePath, filePath, cropdo)
              saveCropped(filePath)
            }
          }
        } else {
          // 如果 map 不包含，则移动该文件到 tmp 目录，同时将同名 txt 文件移动
          moveToTmpSync(filePath, `${num}_${folderName}`, 'not found in map')
        }
      } else if (!isAllowImage && !fileName.toLowerCase().endsWith(TXT_SUFFIX)) {
        // 不允许的图片直接删除
        moveToTmpSync(filePath, `${num}_${folderName}`, 'not allowed')
      }
    }
  }
}

function moveToTmpSync(imageFilePath, targetDir, reason) {
  let fromDir = path.dirname(imageFilePath);
  let fileName = path.basename(imageFilePath);
  let fileExtension = path.extname(imageFilePath);
  let fileNameNoExt = path.basename(imageFilePath, fileExtension);
  let fileNameTxt = `${fileNameNoExt}${TXT_SUFFIX}`
  let txtFilePath = path.join(fromDir, fileNameTxt)

  let destPath = path.join(TMP_DIR, targetDir, fileName)
  let destTxtPath = path.join(TMP_DIR, targetDir, fileNameTxt)
  moveFileSync(imageFilePath, destPath)
  moveFileSync(txtFilePath, destTxtPath)

  log(`doTrim moveToTmpSync image file to ${destPath} reason: ${reason}`)
}

function log(str) {
  if (DEBUG) {
    logger.log(str)
  } else {
    console.log(str)
  }
}
function error(str, error) {
  if (DEBUG) {
    logger.error(str, error)
  } else {
    console.error(str, error)
  }
}

function nowTimeStr() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  const formattedTime = `${year}-${month}-${day}_${hours}-${minutes}-${seconds}`;

  return formattedTime
}

async function copyFilesFromDirectory(sourceDirectory, destinationDirectory) {
  try {
    await fse.copy(sourceDirectory, destinationDirectory);
    console.log('文件拷贝成功');
  } catch (err) {
    console.error('文件拷贝失败:', err);
  }
}

async function mainEntry() {
  if (doTrim && trimParamArr.length >= 4 && localImageDirectory.indexOf('/saved/') > -1) {
    let savedDir = path.join(__dirname, 'saved')

    // localImageDirectory 里的图片要拷贝到 filter 目录
    let relativeImagePath = path.relative(savedDir, localImageDirectory)
    let targetImageDir = path.join(__dirname, 'saled', relativeImagePath)

    await fse.remove(targetImageDir);
    await copyFilesFromDirectory(localImageDirectory, targetImageDir)
    console.log('copying images to directory ./saled/ and then do trim!')
    console.log(`localImageDirectory is ${localImageDirectory} and saledDirectory is ${targetImageDir}`)
    localImageDirectory = targetImageDir

    // readFilePath 数据文件也要拷贝到 saled 目录
    let relativeDataPath = path.relative(savedDir, readFilePath)
    let targetDataPath = path.join(__dirname, 'saled', relativeDataPath)
    console.log(`relativeDataPath is ${relativeDataPath} and targetDataPath is ${targetDataPath}`)
    
    fs.copyFileSync(readFilePath, targetDataPath);
    readFilePath = targetDataPath
  }

  let data = fs.readFileSync(readFilePath, 'utf8');

  // 将 JSON 数据解析为 JavaScript 对象
  itemFullArr = JSON.parse(data);



  log(`!!! total images in metadata ${itemFullArr.length} blocked:${confirmDeleteModelIds.length}`)

  let imageRelativePath = ''
  let resultFilePrefix = ''
  if (targetFilePathPrefix) {
    resultFilePrefix = targetFilePathPrefix
    if (!resultFilePrefix.startsWith('.') && !resultFilePrefix.startsWith('/')) {
      resultFilePrefix = `./${resultFilePrefix}`
    }
    imageRelativePath = path.relative(path.dirname(resultFilePrefix), localImageDirectory)
  }
  
  
  // 注意保持原始数据序号不变，所以用原始列表
  totalSize = itemFullArr.length
  splitArr = []
  for (var i=0; i<splitNum + 1; i++) {
    splitArr.push([])
  }
  for (var j=0; j<totalSize; j++) {
    let idx = Math.floor(j/(Math.floor(totalSize/splitNum)))
    let itemInData = itemFullArr[j]
    let item = await filterItem(itemInData, imageRelativePath)
    if (item) {
      if (useLocalImage) {
        delete item.image_url1
        delete item.image_url2
      }
      
      if (doTrim) {
        // doTrim 需要把 item 放到 map 里
        trimUseMap[item.file_name] = item

        // 扩展 item 参数，主要是裁剪信息
        let editItem = confirmEditMap[item.file_name]
        // log(editItem)
        if (editItem) {
          // crop1  crop2
          let crop1 = editItem[CROP_ARR_1]
          let crop2 = editItem[CROP_ARR_2]
          item[CROP_ARR_1] = crop1
          item[CROP_ARR_2] = crop2
        }

        // log(trimUseMap[item.file_name])
      }

      splitArr[idx].push(item)
    } else {
      // log('filter out! not exits or in deleted array.')
    }
  }

  log(`doTrimMap keys length is ${Object.keys(trimUseMap).length}`)
  if (doTrim && Object.keys(trimUseMap).length <= 0) {
    error(`doTrimMap is empty, cannot continue, please check first.`, 'item not found')
    return
  }



  for (var i=0; i<splitNum; i++) {
    let resultArr = splitArr[i]

    if (doTrim) {
      // 如果是对素材进行处理，将筛选过后的图片素材单独移除，同时加上提词文件
      try {
        await traverseDirectorySyncAndDoTrim(localImageDirectory)
      } catch (err) {
        error('doTrim traverseDirectorySyncAndDoTrim finally error: ', err);
      }
    }



    const htmlText = fs.readFileSync(
      path.resolve(__dirname, templateFilePath),
      "utf-8"
    );

    const newHtml = htmlText.replace(
      /const listJson = '[^']*'/,
      `const listJson = ${JSON.stringify(resultArr)}`
    );

    log(`!!! total images in html ${resultArr.length}`)

    let targetFileName = `${resultFilePrefix}_${i}.html`;
    let htmlPath = path.resolve(targetFileName)
    log(`htmlPath: ${htmlPath}  targetFileName: ${targetFileName}`)
    fs.writeFile(
      htmlPath,
      newHtml,
      "utf-8",
      function (err) {
        if (err) {
          log(err);
        } else {
          log(`生成 ${targetFileName} 完毕!`);
        }
      }
    );
  }

  // 对原始数据文件进行修改
  if (doTrim && itemFullArr.length) {
    itemFullArr = itemFullArr.filter(item => !!trimUseMap[item.file_name])

    itemFullArr.forEach((ele) => {
      delete ele.image_url1
      delete ele.image_url2
      delete ele.image_width
      delete ele.image_height
      delete ele.crop_arr_1
      delete ele.crop_arr_2
      let fileName = ele.file_name
      if (trimUseMap[fileName] && trimUseMap[fileName][PROPMTS_ARR]) {
        ele[PROPMTS_ARR] = trimUseMap[fileName][PROPMTS_ARR]
      }
    })

    // 写入本地文件
    try {
      fs.writeFileSync(readFilePath, JSON.stringify(itemFullArr, null, 2), 'utf8');
      log(`数据已成功写入文件: ${readFilePath}，总数: ${itemFullArr.length}`);
    } catch (err) {
      error('写入文件时发生错误：', err);
    }


    // 写入本地文件 editmap
    try {
      fs.writeFileSync(confirmEditMapFilePath, '{}', 'utf8');

      // 这个文件是累积的，直到 bash 脚本消费掉，在 bash 里置空
      fs.writeFileSync(confirmCroppedFilePath, confirmCroppedList.join('\n'), 'utf8');
    } catch (err) {}
    
    // 写入本地文件 delete
    try {
      // TODO balibell
      // fs.writeFileSync(cofirmDeleteFilePath, '[]', 'utf8');
      // fs.writeFileSync(confirmCroppedFilePath, '[]', 'utf8');
    } catch (err) {}
  }
}








// 起点
mainEntry()
