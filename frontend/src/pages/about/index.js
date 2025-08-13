import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'
import { useState, useEffect } from 'react'

const About = ({ updateOrders, orders }) => {
  const [isVisible, setIsVisible] = useState(false)
  const [typedText, setTypedText] = useState('')
  const fullText = "Привет!"

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 100)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (!isVisible) return

    let currentIndex = 0
    const typingTimer = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setTypedText(fullText.slice(0, currentIndex))
        currentIndex++
      } else {
        clearInterval(typingTimer)
      }
    }, 150)

    return () => clearInterval(typingTimer)
  }, [isVisible])

  const foodFacts = [
    "🍯 Мёд никогда не портится!",
    "🥕 Морковь раньше была фиолетовой",
    "🍌 Бананы - это ягоды!",
    "🧄 Чеснок отпугивает не только вампиров",
    "🍓 Клубника - единственный фрукт с семенами снаружи"
  ]

  const [currentFact, setCurrentFact] = useState(0)

  useEffect(() => {
    const factTimer = setInterval(() => {
      setCurrentFact(prev => (prev + 1) % foodFacts.length)
    }, 3000)

    return () => clearInterval(factTimer)
  }, [])

  const [timeOnSite, setTimeOnSite] = useState(0)

  useEffect(() => {
    const startTime = Date.now()
    const timer = setInterval(() => {
      setTimeOnSite(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>

    <Container>
      <div style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 0.6s ease-out'
      }}>
        <h1 className={styles.title} style={{
          background: 'linear-gradient(45deg, #ff6b35, #f7931e)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          {typedText}
          <span style={{
            opacity: typedText.length < fullText.length ? 1 : 0,
            animation: 'blink 1s infinite'
          }}>|</span>
        </h1>

        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '15px 20px',
          borderRadius: '10px',
          margin: '20px 0',
          textAlign: 'center',
          fontSize: '16px',
          fontWeight: '500',
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
        }}
        onMouseEnter={e => {
          e.target.style.transform = 'scale(1.02)'
          e.target.style.boxShadow = '0 6px 20px rgba(0,0,0,0.15)'
        }}
        onMouseLeave={e => {
          e.target.style.transform = 'scale(1)'
          e.target.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)'
        }}>
          💡 А знаете ли вы? {foodFacts[currentFact]}
        </div>

        <div className={styles.content}>
          <div>
            <h2 className={styles.subtitle} style={{
              position: 'relative',
              paddingLeft: '20px'
            }}>
              <span style={{
                position: 'absolute',
                left: 0,
                top: '50%',
                transform: 'translateY(-50%)',
                width: '4px',
                height: '100%',
                background: 'linear-gradient(to bottom, #ff6b35, #f7931e)',
                borderRadius: '2px'
              }}></span>
              Что это за сайт?
            </h2>
            <div className={styles.text}>
              <p className={styles.textItem} style={{
                borderLeft: '3px solid #ff6b35',
                paddingLeft: '15px',
                background: 'linear-gradient(90deg, rgba(255,107,53,0.05) 0%, transparent 100%)'
              }}>
                Представляю вам проект, созданный во время обучения в Яндекс Практикуме. Этот проект — часть учебного курса, но он создан полностью самостоятельно.
              </p>
              <p className={styles.textItem}>
                Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для
                приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.
              </p>
              <p className={styles.textItem}>
                Чтобы использовать все возможности сайта — нужна регистрация. Проверка адреса электронной почты не осуществляется, вы можете ввести любой email.
              </p>
              <p className={styles.textItem} style={{
                background: 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)',
                padding: '15px',
                borderRadius: '8px',
                color: '#2c3e50',
                fontWeight: '500'
              }}>
                🚀 Заходите и делитесь своими любимыми рецептами!
              </p>
            </div>
          </div>
          <aside>
            <h2 className={styles.additionalTitle}>
              Ссылки
            </h2>
            <div className={styles.text}>
              <p className={styles.textItem}>
                Код проекта находится тут - <a href="https://github.com/Khoetskiy/foodgram" className={styles.textLink} style={{
                  background: 'linear-gradient(45deg, #667eea, #764ba2)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 'bold',
                  textDecoration: 'none',
                  borderBottom: '2px solid #667eea',
                  transition: 'all 0.3s ease'
                }}>Github</a>
              </p>
              <p className={styles.textItem}>
                Автор проекта: <a href="#" className={styles.textLink} style={{
                  background: 'linear-gradient(45deg, #667eea, #764ba2)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  fontWeight: 'bold',
                  textDecoration: 'none',
                  borderBottom: '2px solid #667eea'
                }}>Khoetskiy Sergey</a>
              </p>

              {/* Забавная статистика */}
              <div style={{
                marginTop: '20px',
                padding: '15px',
                background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <p style={{ margin: '5px 0', fontSize: '14px', color: '#8b4513' }}>
                  ⏱️ Вы на сайте уже: <strong>{timeOnSite} сек</strong>
                </p>
                <p style={{ margin: '5px 0', fontSize: '14px', color: '#8b4513' }}>
                  📅 Сегодня: <strong>{new Date().toLocaleDateString('ru-RU')}</strong>
                </p>
                <p style={{ margin: '5px 0', fontSize: '14px', color: '#8b4513' }}>
                  🌟 Ваш визит делает этот сайт лучше!
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>

    </Container>

    <style jsx>{`
      @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
      }
    `}</style>
  </Main>
}

export default About
