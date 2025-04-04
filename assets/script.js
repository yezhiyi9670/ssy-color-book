(() => {{
  const $dialog = document.querySelector('.color-info-dialog')
  const $root = document.querySelector('.root')
  const $html = document.querySelector('html')
  let $lastElement = null

  $dialog.addEventListener('click', evt => {
    document.getSelection().removeAllRanges()
    evt.stopPropagation()
  })
  document.querySelectorAll('.color-display-block').forEach(element => {
    element.addEventListener('click', evt => evt.stopPropagation())
  })

  addEventListener('click', () => {
    closeDialog()
  })
  document.querySelector('.color-info-dialog .close').addEventListener('click', () => {
    closeDialog()
  })

  function closeDialog() {
    if($dialog.style.display == 'none') {
      return
    }
    document.getSelection().removeAllRanges()
    $dialog.style.display = 'none'
  }

  function openDialog(element) {
    $dialog.style.display = 'block';
    
    let left = element.offsetLeft + element.offsetWidth / 2 - $dialog.offsetWidth / 2
    
    let top = element.offsetTop + element.offsetHeight * 1.7

    if(top + $dialog.offsetHeight - $html.scrollTop >= window.innerHeight) {
      top = element.offsetTop - $dialog.offsetHeight - element.offsetHeight * 0.2
    }
    if(left < 0) {
      left = 8
    }
    if(left + $dialog.offsetWidth >= $root.offsetWidth) {
      left = $root.offsetWidth - $dialog.offsetWidth - 8
    }

    let sizeValue = NaN
    const fontSize = getComputedStyle($dialog)['font-size']
    if(fontSize && fontSize.endsWith('px')) {
      sizeValue = +fontSize.substring(0, fontSize.length - 2)
    }
    if(sizeValue == sizeValue) {
      // Ensure consistency on window resize
      $dialog.style.left = left / sizeValue + 'em'
      $dialog.style.top = top / sizeValue + 'em'
    } else {
      $dialog.style.left = left + 'px'
      $dialog.style.top = top + 'px'
    }
  }
  
  function showColorDetails(element, preferHexValue) {
    json_str = element.getAttribute('data-json')
    if(!json_str) {
      return
    }
    data = JSON.parse(json_str.replaceAll('^', '"'))
    if(data.css != '--') {
      document.querySelector('.color-zoomin-block').style.boxShadow = 
        `inset 10em 0 0 0 ${data.css}`
      $dialog.classList.remove('undisplayable')
      document.querySelector('.color-details-row-css .color-value-coord').innerText = data.css
      document.querySelector('.color-details-row-css').classList.remove('invalid')
    } else {
      document.querySelector('.color-zoomin-block').style.boxShadow = 
        `inset 10em 0 0 0 transparent`
      $dialog.classList.add('undisplayable')
      document.querySelector('.color-details-row-css .color-value-coord').innerText = data.css
      document.querySelector('.color-details-row-css').classList.add('invalid')
    }
    if(data.isChromasample) {
      $dialog.classList.add('chromasample')
    } else {
      $dialog.classList.remove('chromasample')
    }
    if(data.cmyk[0]) {
      $dialog.classList.remove('cmyk-unavailable')
    } else {
      $dialog.classList.add('cmyk-unavailable')
    }
    document.querySelector('.color-zoomin-label-i').innerText = data.name

    for(let key of ['srgb', 'adobergb', 'displayp3', 'cmyk', 'xyy', 'ssy']) {
      const [ available, coord, hex ] = data[key]
      const $row = document.querySelector(`.color-details-row-${key}`)
      const $coord = document.querySelector(`.color-details-row-${key} .color-value-coord`)
      const $hex = document.querySelector(`.color-details-row-${key} .color-value-hex`)
      
      if(available) {
        $row.classList.remove('invalid')
      } else {
        $row.classList.add('invalid')
      }
      $coord.innerText = coord
      if($hex) {
        $hex.innerText = hex
      }
    }

    openDialog(element)

    $lastElement = element
    if(preferHexValue) {
      const currentGamut = document.body.getAttribute('data-gamut-identifier')
      document.querySelector(`.color-details-row-${currentGamut} .color-value-hex`).focus()
    } else {
      document.querySelector('.color-zoomin-label-i').focus()
    }
  }
  document.querySelectorAll('.color-display-block').forEach(element => {
    element.setAttribute('href', 'javascript:;')
    element.addEventListener('dragstart', evt => {
      evt.preventDefault()
    })
    element.addEventListener('click', evt => {
      showColorDetails(evt.target, false)
      evt.preventDefault()
    })
    element.addEventListener('contextmenu', evt => {
      showColorDetails(evt.target, true)
      evt.preventDefault()
    })
  })

  document.querySelectorAll('.copy-field').forEach(element => {
    const selectAll = evt => {
      let range = new Range()
      range.selectNode(element)
      document.getSelection().removeAllRanges()
      document.getSelection().addRange(range)
      evt.stopPropagation()
    }
    element.addEventListener('focus', selectAll)
    element.addEventListener('click', selectAll)
  })
  $dialog.addEventListener('keydown', evt => {
    if(evt.key == 'Escape') {
      closeDialog()
      if($lastElement) {
        $lastElement.focus()
      }
    }
  })

  document.querySelectorAll('a').forEach(element => {
    element.addEventListener('click', evt => {
      if(element.classList.contains('link-active')) {
        evt.preventDefault()
      }
    })
  })

  document.body.setAttribute('data-cmyk-mode', 'mark')
  function set_cmyk_mode(flag) {
    document.body.setAttribute('data-cmyk-mode', flag)
    document.querySelectorAll('.cmyk-mode').forEach(element => {
      element.classList.remove('link-active')
    })
    document.querySelector(`.cmyk-mode[data-cmyk-mode=${flag}]`).classList.add('link-active')
  }
  document.querySelectorAll('.cmyk-mode').forEach(element => {
    element.addEventListener('click', () => {
      set_cmyk_mode(element.getAttribute('data-cmyk-mode'))
    })
  })

  document.body.setAttribute('data-aug-mode', 'hide')
  function set_aug_mode(flag) {
    document.body.setAttribute('data-aug-mode', flag)
    document.querySelectorAll('.aug-mode').forEach(element => {
      element.classList.remove('link-active')
    })
    document.querySelector(`.aug-mode[data-aug-mode=${flag}]`).classList.add('link-active')
  }
  document.querySelectorAll('.aug-mode').forEach(element => {
    element.addEventListener('click', () => {
      set_aug_mode(element.getAttribute('data-aug-mode'))
    })
  })
}})()
