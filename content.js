/* =====================================================================
   SOVEREIGN 5-SYSTEM CONTENT LIBRARY  —  content.js
   Bilingual Edition: English (EN) & Spanish (ES)
   All interpretive copy and UI localization lives here.
   ===================================================================== */
(function (root) {
  'use strict';

  /* ===================================================================
     1–9 MASTER ARCHETYPES (ENGLISH & SPANISH)
     =================================================================== */
  const ARCHETYPES_EN = {
    1: {
      name: 'The Sovereign', ruler: 'Sun', keywords: ['Initiative', 'Autonomy', 'Command'],
      core: 'You are an originator. Your code is built around self-authored will: the first move, the clean decision, the willingness to stand alone at the front of the room. When 1 anchors a profile across multiple ancient systems, it signals a person meant to lead rather than follow, to found rather than join. Your power multiplies the moment you stop asking for permission.',
      wealth: 'You materialize abundance by owning the origin point: your own brand, your own IP, your own equity. Salaried roles cap you; founder seats, first-mover positions and personal authority compound for you. Money follows your decisiveness. Hesitation is the single most expensive habit in your chart.',
      foundation: 'Your grounding mechanism is autonomy. You stabilize when you hold the final decision and destabilize when your direction is dictated by committee. Boundary rule: consult widely, decide alone.',
      shadow: 'Isolation, stubbornness and an ego that refuses counsel.',
      soul: 'At heart you crave independence and the dignity of building something unmistakably yours.',
      persona: 'Others read you as confident, direct and self-contained, sometimes intimidating on first contact.',
      magnetism: 'You attract through certainty. Speak in decisions, not possibilities.',
      tactics: ['Launch before you feel ready. The 1 vibration rewards motion over perfection.', 'Keep equity and naming rights wherever possible.', 'Schedule your highest-stakes decisions on Sundays (the Solar day).'],
    },
    2: {
      name: 'The Oracle', ruler: 'Moon', keywords: ['Intuition', 'Alliance', 'Timing'],
      core: 'You are a reader of undercurrents. Your code is tuned to the subtle: tone, timing, the unspoken need in a room. A dominant 2 marks the strategist behind the throne, the partner who makes empires possible, the one who senses the shift before the data confirms it. Your sensitivity is not a weakness. It is an instrument.',
      wealth: 'You materialize abundance through partnership and timing: joint ventures, brokering, mediation, key-client relationships and patient entries. Your wealth is relational. The right alliance is worth more to you than any solo sprint.',
      foundation: 'Your grounding is rhythm and sanctuary. Protect your sleep, your quiet hours and your inner circle. Boundary rule: you may feel everyone\'s emotions, but you are only responsible for your own.',
      shadow: 'Indecision, people-pleasing and over-dependence on approval.',
      soul: 'You long for deep union, harmony and to be understood without having to explain yourself.',
      persona: 'Others see you as gentle, perceptive and easy to trust.',
      magnetism: 'You attract by listening. People feel seen in your presence. Use that deliberately.',
      tactics: ['Before any major move, sleep on it. Your intuition processes overnight.', 'Pair with a decisive 1, 8 or 9 operator to execute your insights.', 'Make key partnership calls on Mondays (the Lunar day).'],
    },
    3: {
      name: 'The Herald', ruler: 'Jupiter', keywords: ['Expression', 'Expansion', 'Wisdom'],
      core: 'You are a voice. Your code expands whatever it touches: ideas, rooms, audiences. A dominant 3 is the teacher, the storyteller, the visionary communicator whose words carry Jupiterian weight. You were built to be heard, and your growth accelerates every time you publish, speak or teach.',
      wealth: 'You materialize abundance through audience and expression: content, teaching, writing, sales presentations and brand storytelling. Your wealth scales with your visibility. Every piece of authentic expression is a seed that compounds.',
      foundation: 'Your grounding is structured creativity. Without a container your gifts scatter. Boundary rule: one primary channel, one core message, repeated until it becomes inevitable.',
      shadow: 'Scattered energy, unfinished projects and words that outrun action.',
      soul: 'You crave joy, creative freedom and an audience for the ideas burning inside you.',
      persona: 'Others experience you as charismatic, warm, witty and optimistic.',
      magnetism: 'You attract by sharing. Teach what you know publicly and the right people find you.',
      tactics: ['Publish daily. Your number rewards consistent expression.', 'Turn your knowledge into a teachable framework or course.', 'Pitch and negotiate on Thursdays (Jupiter\'s day).'],
    },
    4: {
      name: 'The Architect', ruler: 'Rahu', keywords: ['Structure', 'Discipline', 'Breakthrough'],
      core: 'You are a builder of systems. Your code is engineered for structure: process, order and the patient stacking of bricks that others are too restless to lay. Through its Vedic ruler Rahu, the 4 also carries an unconventional edge. You rebuild broken systems in ways nobody else considered, and what you build tends to outlast you.',
      wealth: 'You materialize abundance through systems and assets: operations, real estate, infrastructure, automated processes and compounding portfolios. Your wealth is slow-built and hard to destroy. You win by refusing to stop.',
      foundation: 'Your grounding is routine. Written plans, fixed rituals and clean environments are not optional for you; they are your power source. Boundary rule: protect the schedule and the schedule protects you.',
      shadow: 'Rigidity, overwork and resistance to necessary change.',
      soul: 'You long for security, order and the deep satisfaction of a job done properly.',
      persona: 'Others read you as reliable, serious and quietly formidable.',
      magnetism: 'You attract through dependability. Being the one who always delivers is your quiet luxury.',
      tactics: ['Document every repeatable task into a system, then delegate it.', 'Favor real assets and long-horizon positions.', 'Do your restructuring and planning on Saturdays.'],
    },
    5: {
      name: 'The Navigator', ruler: 'Mercury', keywords: ['Commerce', 'Adaptability', 'Velocity'],
      core: 'You are a mover. Your code is built for velocity: trade, travel, conversation and the fast pivot. A dominant 5 marks the merchant-navigator who reads markets in real time and thrives where others freeze. You sit at the centre of the Lo Shu square for a reason: everything flows through you.',
      wealth: 'You materialize abundance through commerce and velocity: sales, trading, arbitrage, marketing, deal-flow and multiple income streams. Money must move for you. Stagnant capital and stagnant careers both drain your field.',
      foundation: 'Your grounding is freedom with rules. You need movement, but you also need a few non-negotiable anchors to stop it becoming chaos. Boundary rule: change your tactics freely, never your core principles.',
      shadow: 'Restlessness, excess and abandoning things right before they pay off.',
      soul: 'You crave freedom, variety and the thrill of the new horizon.',
      persona: 'Others see you as clever, quick, curious and magnetic in conversation.',
      magnetism: 'You attract by being interesting. Your stories and range open doors.',
      tactics: ['Build at least three income streams. Your number dislikes single points of failure.', 'Set hard risk rules before entering any high-velocity opportunity.', 'Close deals on Wednesdays (Mercury\'s day).'],
    },
    6: {
      name: 'The Magnetic Steward', ruler: 'Venus', keywords: ['Magnetism', 'Luxury', 'Responsibility'],
      core: 'You are a magnet. Your code is tuned to beauty, harmony and responsibility: the Venusian gift of making people, places and brands feel valuable. A dominant 6 marks the steward who elevates everything in their care. People trust you instinctively, and trust is the rarest currency there is.',
      wealth: 'You materialize abundance through premium positioning: luxury, design, hospitality, beauty, advisory and high-trust service. You are paid for taste and care, so never discount either. Raise your prices and refine your presentation.',
      foundation: 'Your grounding is home and aesthetics. A beautiful, ordered environment restores you. Boundary rule: give generously, but never from an empty vault.',
      shadow: 'Martyrdom, perfectionism and over-responsibility for others.',
      soul: 'You long to love and be loved, to create beauty and to protect your people.',
      persona: 'Others read you as warm, elegant, caring and deeply trustworthy.',
      magnetism: 'You attract through presence and taste. Curate how you look, speak and present your work.',
      tactics: ['Position everything you sell in the premium tier.', 'Invest in your environment and personal presentation. It is ROI for you.', 'Host, launch and network on Fridays (Venus\'s day).'],
    },
    7: {
      name: 'The Analyst', ruler: 'Ketu', keywords: ['Depth', 'Pattern', 'Mastery'],
      core: 'You are a seeker of hidden structure. Your code is built for depth: research, analysis and the pattern that sits underneath the noise. A dominant 7 marks the specialist, the quiet investor, the mystic-scientist who sees what the crowd misses. Your edge is insight, and insight cannot be copied.',
      wealth: 'You materialize abundance through specialized expertise and asymmetric insight: research, data, technology, niche mastery and contrarian positions. You win by knowing more than the room, then acting quietly before consensus arrives.',
      foundation: 'Your grounding is solitude and study. Silence is not loneliness for you; it is recharge. Boundary rule: protect your deep-work hours as fiercely as your capital.',
      shadow: 'Withdrawal, suspicion and analysis paralysis.',
      soul: 'You crave truth, understanding and the space to think without interruption.',
      persona: 'Others experience you as reserved, intelligent and somewhat mysterious.',
      magnetism: 'You attract through mystique. Say less, reveal depth selectively, and people lean in.',
      tactics: ['Build an edge in one niche until you are the reference point.', 'Decide from data and pattern, then commit. Avoid endless research loops.', 'Reserve Tuesdays for deep analysis and review.'],
    },
    8: {
      name: 'The Magnate', ruler: 'Saturn', keywords: ['Authority', 'Capital', 'Endurance'],
      core: 'You are built for power and material mastery. Your code carries Saturn\'s authority: long horizons, high stakes, karmic weight. A dominant 8 is the Chinese number of supreme wealth (Fa) and the Vedic Yogakaraka engine: the executive, the capital allocator, the one who is tested early so they can hold more later. Pressure is your forge.',
      wealth: 'You materialize abundance through scale and capital: ownership, leverage, equity, executive authority and long-term compounding. You are meant to steward large resources, and your wealth arrives in proportion to your integrity and patience.',
      foundation: 'Your grounding is karmic balance. Clean deals, honest books and long-term thinking keep your engine running. Boundary rule: never trade your integrity for speed.',
      shadow: 'Control, workaholism and measuring self-worth by net worth.',
      soul: 'You crave achievement, respect and the security of true financial sovereignty.',
      persona: 'Others read you as powerful, competent and authoritative: a natural executive.',
      magnetism: 'You attract through gravitas. Move slower, speak with certainty, and let results speak.',
      tactics: ['Think in ten-year horizons. Saturn rewards the patient.', 'Own assets, not just income. Prioritize equity and capital allocation.', 'Sign contracts and review finances on Saturdays.'],
    },
    9: {
      name: 'The Sage-Warrior', ruler: 'Mars', keywords: ['Courage', 'Completion', 'Mission'],
      core: 'You are the completion of the cycle. Your code contains every number before it: breadth, courage and a mission larger than yourself. Ruled by Mars in the Vedic system and Fire in the Lo Shu, a dominant 9 marks the warrior-humanitarian whose influence spreads wide. You were built to finish what others start and to lead with conviction.',
      wealth: 'You materialize abundance through mission and execution: movements, large audiences, global markets and bold action. Money comes to you as fuel for a cause. The bigger the vision, the more resources gather around it.',
      foundation: 'Your grounding is release. You stabilize when you finish and let go of what is complete. Boundary rule: close every loop and never carry yesterday\'s battles into today.',
      shadow: 'Burnout, martyrdom and holding on to what has already ended.',
      soul: 'You long to make a meaningful impact and to leave the world better than you found it.',
      persona: 'Others see you as passionate, generous, bold and worldly.',
      magnetism: 'You attract through conviction. Stand for something publicly.',
      tactics: ['Tie every business goal to a larger mission statement.', 'Act fast once decided. Mars punishes hesitation.', 'Launch bold initiatives on Tuesdays (Mars\'s day).'],
    },
  };

  const ARCHETYPES_ES = {
    1: {
      name: 'El Soberano', ruler: 'Sol', keywords: ['Iniciativa', 'Autonomía', 'Mando'],
      core: 'Eres un originador. Tu código está construido sobre la voluntad propia: el primer movimiento, la decisión limpia, la disposición a estar solo al frente de la sala. Cuando el 1 ancla un perfil en múltiples sistemas antiguos, señala a una persona destinada a liderar antes que a seguir, a fundar antes que a unirse. Tu poder se multiplica en el momento en que dejas de pedir permiso.',
      wealth: 'Materializas la abundancia siendo dueño del punto de origen: tu propia marca, tu propiedad intelectual, tu capital propio. Los roles asalariados te limitan; los asientos de fundador, las posiciones pioneras y la autoridad personal generan interés compuesto para ti. El dinero sigue a tu determinación. La vacilación es el hábito más costoso en tu carta.',
      foundation: 'Tu mecanismo de anclaje es la autonomía. Te estabilizas cuando sostienes la decisión final y te desestabilizas cuando tu rumbo lo dicta un comité. Regla de límites: consulta ampliamente, decide en soledad.',
      shadow: 'Aislamiento, terquedad y un ego que rechaza el consejo.',
      soul: 'En el fondo anhelas independencia y la dignidad de construir algo indiscutiblemente tuyo.',
      persona: 'Otros te perciben como seguro, directo y autosuficiente, a veces intimidante en el primer contacto.',
      magnetism: 'Atraes a través de la certeza. Habla en decisiones, no en posibilidades.',
      tactics: ['Lanza antes de sentirte listo. La vibración 1 recompensa la acción sobre la perfección.', 'Conserva la participación accionaria y los derechos de denominación siempre que sea posible.', 'Programa tus decisiones de mayor riesgo los domingos (el día Solar).'],
    },
    2: {
      name: 'El Oráculo', ruler: 'Luna', keywords: ['Intuición', 'Alianza', 'Ritmo'],
      core: 'Eres un lector de corrientes subterráneas. Tu código está afinado para lo sutil: tono, ritmo, la necesidad tácita en una habitación. Un 2 dominante marca al estratega detrás del trono, al socio que hace posibles los imperios, a quien percibe el cambio antes de que los datos lo confirmen. Tu sensibilidad no es una debilidad: es un instrumento de precisión.',
      wealth: 'Materializas la abundancia mediante alianzas estratégicas y sincronización: empresas conjuntas, intermediación, mediación, relaciones clave y entradas pacientes. Tu riqueza es relacional. La alianza correcta vale más para ti que cualquier esfuerzo en solitario.',
      foundation: 'Tu anclaje es el ritmo y el santuario. Protege tu sueño, tus horas de silencio y tu círculo íntimo. Regla de límites: puedes sentir las emociones de todos, pero solo eres responsable de las tuyas.',
      shadow: 'Indecisión, complacencia y excesiva dependencia de la aprobación ajena.',
      soul: 'Anhelas una unión profunda, armonía y ser comprendido sin necesidad de dar explicaciones.',
      persona: 'Otros te perciben como alguien apacible, perceptivo y fácil de confiar.',
      magnetism: 'Atraes escuchando. La gente se siente vista en tu presencia. Utilízalo con deliberación.',
      tactics: ['Antes de cualquier movimiento importante, consúltalo con la almohada. Tu intuición procesa de noche.', 'Asóciate con un operador decidido (1, 8 o 9) para ejecutar tus visiones.', 'Realiza las llamadas estratégicas de asociación los lunes (el día Lunar).'],
    },
    3: {
      name: 'El Heraldo', ruler: 'Júpiter', keywords: ['Expresión', 'Expansión', 'Sabiduría'],
      core: 'Eres una voz. Tu código expande todo lo que toca: ideas, salas, audiencias. Un 3 dominante es el maestro, el narrador, el comunicador visionario cuyas palabras tienen peso jupiteriano. Fuiste hecho para ser escuchado, y tu crecimiento se acelera cada vez que publicas, hablas o enseñas.',
      wealth: 'Materializas la abundancia a través de la audiencia y la expresión: contenido, formación, escritura, presentaciones comerciales y narrativa de marca. Tu riqueza escala con tu visibilidad. Cada expresión auténtica es una semilla que genera interés compuesto.',
      foundation: 'Tu anclaje es la creatividad estructurada. Sin un contenedor tus talentos se dispersan. Regla de límites: un canal principal, un mensaje central, repetido hasta volverse inevitable.',
      shadow: 'Energía dispersa, proyectos inconclusos y palabras que corren más rápido que los hechos.',
      soul: 'Anhelas alegría, libertad creativa y una audiencia receptiva para las visiones que arden en tu interior.',
      persona: 'Otros te experimentan como carismático, cálido, ingenioso y magnéticamente optimista.',
      magnetism: 'Atraes compartiendo. Enseña lo que sabes públicamente y las personas correctas te encontrarán.',
      tactics: ['Publica a diario. Tu vibración premia la expresión sostenida.', 'Transforma tu conocimiento en un marco metodológico o programa formativo.', 'Negocia y presenta propuestas clave los jueves (el día de Júpiter).'],
    },
    4: {
      name: 'El Arquitecto', ruler: 'Rahu', keywords: ['Estructura', 'Disciplina', 'Innovación'],
      core: 'Eres un constructor de sistemas. Tu código está diseñado para la estructura: procesos, orden y la colocación paciente de cimientos que otros no se detienen a asentar. Mediante su regente védico Rahu, el 4 también aporta una agudeza no convencional. Reconstruyes sistemas quebrados de formas que nadie más consideró, y lo que edificas perdura en el tiempo.',
      wealth: 'Materializas la abundancia a través de sistemas y activos: operaciones, bienes raíces, infraestructura, procesos automatizados y carteras con interés compuesto. Tu riqueza se forja con paciencia y es difícil de destruir. Ganas negándote a detenerte.',
      foundation: 'Tu anclaje es la rutina. Los planes por escrito, los rituales fijos y los entornos impecables no son opcionales; son tu fuente de poder. Regla de límites: protege la agenda y la agenda te protegerá a ti.',
      shadow: 'Rigidez, exceso de trabajo y resistencia a los cambios necesarios.',
      soul: 'Anhelas seguridad, orden y la profunda satisfacción de una obra impecablemente ejecutada.',
      persona: 'Otros te leen como alguien confiable, formal y discretamente formidable.',
      magnetism: 'Atraes por tu solvencia. Ser quien siempre cumple su palabra es tu verdadero lujo silencioso.',
      tactics: ['Documenta cada proceso repetible en un sistema formal, luego delégalo.', 'Privilegia activos reales y posiciones con horizontes de largo plazo.', 'Dedica los sábados a reestructurar y planificar estratégicamente.'],
    },
    5: {
      name: 'El Navegante', ruler: 'Mercurio', keywords: ['Comercio', 'Adaptabilidad', 'Velocidad'],
      core: 'Eres un operador del movimiento. Tu código está diseñado para la velocidad: comercio, viajes, negociación y el giro rápido. Un 5 dominante marca al mercader-navegante que lee los mercados en tiempo real y prospera donde otros se paralizan. Te sitúas en el centro del cuadrado Lo Shu por una razón: todo fluye a través de ti.',
      wealth: 'Materializas la abundancia mediante el comercio y la velocidad: ventas, trading, arbitraje, marketing, flujo de tratos y múltiples fuentes de ingreso. El dinero debe circular para ti. El capital inmóvil drena tu campo.',
      foundation: 'Tu anclaje es la libertad con reglas. Requieres movimiento, pero también necesitas límites infranqueables para evitar el caos. Regla de límites: flexibiliza tus tácticas libremente, jamás tus principios.',
      shadow: 'Inquietud, dispersión y abandono de proyectos justo antes de que rindan fruto.',
      soul: 'Anhelas libertad absoluta, variedad y la adrenalina de nuevos horizontes.',
      persona: 'Otros te perciben como ágil, elocuente, curioso y magnético en cualquier conversación.',
      magnetism: 'Atraes siendo interesante. Tus vivencias y rango de visión abren puertas de inmediato.',
      tactics: ['Construye al menos tres fuentes de ingresos. Tu frecuencia penaliza los puntos únicos de fallo.', 'Define reglas estrictas de riesgo antes de entrar en oportunidades de alta velocidad.', 'Cierra acuerdos comerciales los miércoles (el día de Mercurio).'],
    },
    6: {
      name: 'El Guardián Magnético', ruler: 'Venus', keywords: ['Magnetismo', 'Lujo', 'Responsabilidad'],
      core: 'Eres un imán. Tu código está sintonizado con la belleza, la armonía y la responsabilidad: el don venusino de hacer que personas, espacios y marcas se sientan valiosos. Un 6 dominante marca al custodio que eleva todo lo que está bajo su cuidado. La gente confía en ti por instinto, y la confianza es la divisa más escasa del mundo.',
      wealth: 'Materializas la abundancia a través del posicionamiento de alta gama: lujo, diseño, hospitalidad, belleza, consultoría de alto nivel y servicios de máxima confianza. Te pagan por tu criterio estético y esmero; jamás rebajes ninguno de los dos. Eleva tus tarifas y refina tu presentación.',
      foundation: 'Tu anclaje es el hogar y la estética. Un entorno bello y ordenado restaura tu vitalidad. Regla de límites: entrega con generosidad, pero nunca desde una bóveda vacía.',
      shadow: 'Auto-sacrificio, perfeccionismo y asumir cargas que no te corresponden.',
      soul: 'Anhelas amar y ser amado, crear belleza y proteger a los tuyos.',
      persona: 'Otros te ven como alguien cálido, elegante, protector y digno de absoluta confianza.',
      magnetism: 'Atraes mediante tu presencia y gusto impecable. Cuida meticulosamente tu imagen, oratoria y la presentación de tu obra.',
      tactics: ['Posiciona todas tus ofertas en el segmento prémium.', 'Invierte en tu entorno físico y presentación personal: representa un ROI directo para ti.', 'Organiza eventos, lanzamientos y conexiones clave los viernes (el día de Venus).'],
    },
    7: {
      name: 'El Analista', ruler: 'Ketu', keywords: ['Profundidad', 'Patrón', 'Maestría'],
      core: 'Eres un buscador de la arquitectura oculta. Tu código está forjado para la profundidad: investigación, análisis y el patrón que subyace al ruido superficial. Un 7 dominante marca al especialista, al inversor discreto, al científico-místico que ve lo que la multitud pasa por alto. Tu ventaja es la clarividencia analítica, y esa ventaja no se puede replicar.',
      wealth: 'Materializas la abundancia mediante la especialización técnica y la visión asimétrica: investigación, datos, tecnología, dominio de nichos y apuestas contrarias al consenso. Ganas sabiendo más que el resto de la sala, y actuando con discreción antes de que el mercado se entere.',
      foundation: 'Tu anclaje es la soledad y el estudio riguroso. El silencio no es aislamiento para ti; es recarga de combustible cognitivo. Regla de límites: defiende tus horas de trabajo profundo tan celosamente como tu capital.',
      shadow: 'Distanciamiento excesivo, suspicacia y parálisis por análisis.',
      soul: 'Anhelas la verdad, la comprensión profunda y el espacio para reflexionar sin interrupciones.',
      persona: 'Otros te experimentan como reservado, sumamente inteligente y dotado de un aura misteriosa.',
      magnetism: 'Atraes a través del misterio. Di menos, revela profundidad selectivamente, y captarás toda la atención.',
      tactics: ['Desarrolla una ventaja única en un nicho hasta convertirte en el punto de referencia absoluto.', 'Decide en base a datos y patrones, luego comprométete sin vacilar. Evita bucles infinitos de investigación.', 'Reserva los martes para el análisis profundo, la auditoría y la revisión estratégica.'],
    },
    8: {
      name: 'El Magnate', ruler: 'Saturno', keywords: ['Autoridad', 'Capital', 'Resistencia'],
      core: 'Fuiste forjado para el poder y el dominio material. Tu código porta la autoridad de Saturno: horizontes lejanos, grandes apuestas, peso kármico. Un 8 dominante es el número chino de la suprema riqueza (Fa, 發) y el motor yóguico Yogakaraka: el ejecutivo, el asignador de capital, quien es probado temprano para poder sostener imperios más tarde. La presión es tu fragua.',
      wealth: 'Materializas la abundancia a través de la escala y el capital: propiedad, apalancamiento, acciones, autoridad ejecutiva y acumulación a largo plazo. Estás destinado a administrar grandes recursos, y tu riqueza llega en proporción exacta a tu paciencia e integridad.',
      foundation: 'Tu anclaje es el equilibrio kármico. Tratos limpios, libros contables impecables y pensamiento a largo plazo mantienen tu motor encendido. Regla de límites: nunca canjees tu integridad por velocidad.',
      shadow: 'Control obsesivo, adicción al trabajo y medir el valor personal por el patrimonio neto.',
      soul: 'Anhelas el logro indiscutible, el respeto ganado y la seguridad de la auténtica soberanía financiera.',
      persona: 'Otros te leen como una figura poderosa, altamente competente y de autoridad natural.',
      magnetism: 'Atraes mediante gravitas. Muévete con deliberación, habla con certeza y deja que los resultados hablen.',
      tactics: ['Piensa en horizontes de diez años. Saturno premia a quien sabe esperar.', 'Sé dueño de activos, no solo de ingresos. Prioriza la equidad y la asignación inteligente de capital.', 'Firma contratos y revisa tus finanzas los sábados (el día de Saturno).'],
    },
    9: {
      name: 'El Guerrero Sabio', ruler: 'Marte', keywords: ['Coraje', 'Culminación', 'Misión'],
      core: 'Eres la culminación del ciclo numérico. Tu código contiene cada cifra previa: amplitud, coraje y una causa superior a ti mismo. Regido por Marte en el sistema védico y por el Fuego en el Lo Shu, un 9 dominante señala al líder humanitario cuya influencia trasciende fronteras. Naciste para culminar lo que otros inician y para mandar con convicción.',
      wealth: 'Materializas la abundancia mediante la misión y la ejecución impecable: movimientos, grandes audiencias, mercados internacionales y acción audaz. El dinero llega a ti como combustible para un propósito. Cuanto más grande sea la visión, más recursos gravitarán a su alrededor.',
      foundation: 'Tu anclaje es el desapego y el cierre. Te estabilizas cuando concluyes etapas y sueltas lo terminado. Regla de límites: cierra cada ciclo y jamás arrastres las batallas de ayer al presente.',
      shadow: 'Agotamiento extremo, victimismo y apego a lo que ya cumplió su ciclo.',
      soul: 'Anhelas generar un impacto transformador y dejar el mundo en mejor estado del que encontraste.',
      persona: 'Otros te perciben como apasionado, generoso, valiente y de visión global.',
      magnetism: 'Atraes por tu firmeza de convicciones. Toma postura públicamente por tus principios.',
      tactics: ['Vincula cada objetivo comercial a una declaración de misión trascendente.', 'Actúa con rapidez una vez tomada la decisión. Marte penaliza la duda.', 'Lanza iniciativas audaces los martes (el día de Marte).'],
    },
  };

  /* ===================================================================
     CHALDEAN COMPOUND NUMBERS 10–52
     =================================================================== */
  const COMPOUND_BASE_EN = {
    10: { title: 'The Wheel of Fortune', tone: 'favorable', text: 'Honor, faith and self-confidence. Your name will be known for good or ill according to your desires; plans tend to be carried out.' },
    11: { title: 'The Clenched Hand', tone: 'caution', text: 'A warning of hidden trials and treachery from others. Great strength is available, but it must be guarded with discernment.' },
    12: { title: 'The Sacrifice', tone: 'caution', text: 'Suffering and anxiety through the plans or intrigues of others. The lesson is to protect your own agenda.' },
    13: { title: 'Regeneration', tone: 'power', text: 'Change, power and transformation. Not unlucky: it is the number of upheaval that clears the ground for a new order. Wield it deliberately.' },
    14: { title: 'Movement', tone: 'mixed', text: 'Combinations of people and things, dealings with the public and changing fortunes. Fortunate in commerce, but caution with speculation is advised.' },
    15: { title: 'The Magician', tone: 'favorable', text: 'Eloquence, magnetism and the gift of attracting money, favors and gifts from others. Highly fortunate when used for constructive ends.' },
    16: { title: 'The Shattered Citadel', tone: 'caution', text: 'A forewarning of sudden reversals and the collapse of over-extended plans. Build humbly and verify the ground beneath you.' },
    17: { title: 'The Star of the Magi', tone: 'favorable', text: 'Peace, love and spiritual elevation. You rise above early trials, and your name tends to live on after you. A highly fortunate compound.' },
    18: { title: 'Materialism vs. Spirit', tone: 'caution', text: 'Bitter quarrels, deception and conflict between material and spiritual aims. Prioritize integrity to neutralize it.' },
    19: { title: 'The Prince of Heaven', tone: 'favorable', text: 'Success, esteem and honor. One of the most fortunate compounds: happiness and fulfilment in plans for the future.' },
    20: { title: 'The Awakening', tone: 'mixed', text: 'A new purpose, a call to action for a great cause. Rewards are less material than spiritual, but the calling is unmistakable.' },
    21: { title: 'The Crown of the Magi', tone: 'favorable', text: 'Advancement, honor, elevation and victory after a long struggle. Final success is assured through persistence.' },
    22: { title: 'Submission & Caution', tone: 'caution', text: 'A good person blinded by the folly of others. Beware false judgement and illusion; verify before you trust.' },
    23: { title: 'The Royal Star of the Lion', tone: 'favorable', text: 'Success, help from superiors and protection from those in high places. A supremely fortunate compound for ambition.' },
    24: { title: 'Love, Money & Creativity', tone: 'favorable', text: 'Assistance and association with those of rank and position. Gain through love, partnerships and creative ventures.' },
    25: { title: 'Strength Through Experience', tone: 'favorable', text: 'Benefit gained through observation of people and events. Early trials give way to success that is earned and lasting.' },
    26: { title: 'Partnerships Warning', tone: 'caution', text: 'Grave warnings for the future: ruin through bad advice, poor associates and reckless speculation. Choose partners with extreme care.' },
    27: { title: 'The Sceptre', tone: 'favorable', text: 'Authority, command and reward from the productive intellect. Creative faculties sow good seeds that will yield a harvest.' },
    28: { title: 'Contradictions', tone: 'caution', text: 'Great promise that may be lost through trust in others, opposition in trade, and competition. Prepare for the future and keep reserves.' },
    29: { title: 'Uncertainties', tone: 'caution', text: 'Treachery and deception from others, unexpected dangers and unreliable friends. Strong discernment is your protection.' },
    30: { title: 'Thoughtful Deduction', tone: 'mixed', text: 'Mental superiority, retrospection and deep analysis. Neither fortunate nor unfortunate: its outcome depends entirely on your intent.' },
    31: { title: 'The Recluse', tone: 'mixed', text: 'Self-contained, lonely and isolated from others. Excellent for focused mastery, less so for worldly popularity.' },
    32: { title: 'The Magical Combination', tone: 'favorable', text: 'Magical power akin to 5, 14 and 23. Fortunate if you hold to your own judgement and are not swayed by the stubbornness of others.' },
    37: { title: 'The Fortunate Alliance', tone: 'favorable', text: 'Good and fortunate friendships, love and partnerships. A highly favorable compound for collaboration and magnetism.' },
    43: { title: 'Revolution', tone: 'caution', text: 'Upheaval, strife and revolution. Failure and prevention of plans unless channelled into constructive reform.' },
    51: { title: 'The Warrior', tone: 'power', text: 'A powerful warrior nature promising sudden advancement in whatever is undertaken, but enemies may gather. Guard your rise.' },
  };

  const COMPOUND_BASE_ES = {
    10: { title: 'La Rueda de la Fortuna', tone: 'favorable', text: 'Honor, fe y autoconfianza. Los planes se materializan; tu nombre será reconocido por su impacto constructivo.' },
    11: { title: 'La Mano Cerrada', tone: 'caution', text: 'Advertencia de pruebas ocultas y traición de terceros. Existe un gran poder latente, pero debe custodiarse con discernimiento.' },
    12: { title: 'El Sacrificio', tone: 'caution', text: 'Ansiedad o postergación derivada de intrigas ajenas. La lección vital es proteger tu propia agenda y soberanía.' },
    13: { title: 'Regeneración', tone: 'power', text: 'Transformación radical y poder renovador. Es el número de la ruptura que despeja el terreno para un nuevo orden superior.' },
    14: { title: 'Movimiento', tone: 'mixed', text: 'Interacción con el público, comercio y circunstancias dinámicas. Favorable para los negocios, pero exige prudencia con la especulación.' },
    15: { title: 'El Mago', tone: 'favorable', text: 'Elocuencia suprema, magnetismo y el don de atraer recursos, favores y capital de otros. Sumamente próspero para fines constructivos.' },
    16: { title: 'La Ciudadela Rota', tone: 'caution', text: 'Advertencia de giros inesperados y colapso de planes sobredimensionados. Construye con humildad y verifica el terreno donde pisas.' },
    17: { title: 'La Estrella de los Magos', tone: 'favorable', text: 'Paz, elevación espiritual y trascendencia. Superas los desafíos tempranos y tu legado perdura. Compuesto de altísima fortuna.' },
    18: { title: 'Materia vs. Espíritu', tone: 'caution', text: 'Conflicto entre objetivos materiales y espirituales. Prioriza la transparencia e integridad para disolver cualquier fricción.' },
    19: { title: 'El Príncipe Celestial', tone: 'favorable', text: 'Éxito, estima y honor indiscutible. Uno de los compuestos más afortunados: victoria y realización en planes de futuro.' },
    20: { title: 'El Despertar', tone: 'mixed', text: 'Un nuevo propósito trascendente; llamado a servir a una causa noble. Las recompensas son ante todo de realización personal y propósito.' },
    21: { title: 'La Corona de los Magos', tone: 'favorable', text: 'Ascenso, distinción y victoria tras una larga perseverancia. El éxito duradero está garantizado por tu constancia.' },
    22: { title: 'Sumisión y Cautela', tone: 'caution', text: 'Riesgo de confiar ciegamente en el criterio erróneo de terceros. Mantén tu lucidez y verifica antes de depositar confianza.' },
    23: { title: 'La Estrella Real del León', tone: 'favorable', text: 'Protección de personas en altas esferas y respaldo de líderes. Compuesto sumamente afortunado para la ambición estratégica.' },
    24: { title: 'Amor, Capital y Creación', tone: 'favorable', text: 'Asociación y apoyo de figuras influyentes. Ganancias a través de colaboraciones estratégicas y proyectos creativos.' },
    25: { title: 'Fuerza por la Experiencia', tone: 'favorable', text: 'Sabiduría ganada mediante la observación lúcida del entorno. Los retos iniciales dan paso a un éxito ganado y duradero.' },
    26: { title: 'Alerta de Sociedades', tone: 'caution', text: 'Advertencia severa ante especulación imprudente y malos asesores. Selecciona a tus socios y consejeros con absoluto rigor.' },
    27: { title: 'El Cetro', tone: 'favorable', text: 'Autoridad, mando y recompensas derivadas del intelecto productivo. Tus facultades creativas siembran cosechas abundantes.' },
    28: { title: 'Contradicciones', tone: 'caution', text: 'Gran potencial que puede diluirse por exceso de confianza en otros o competencia desleal. Construye reservas sólidas.' },
    29: { title: 'Incertidumbres', tone: 'caution', text: 'Riesgo de falsas lealtades o giros inesperados de asociados. Tu discernimiento implacable es tu mejor blindaje.' },
    30: { title: 'Deducción Reflexiva', tone: 'mixed', text: 'Superioridad intelectual, retrospectiva y análisis profundo. Su desenlace depende totalmente de la intención con que lo emplees.' },
    31: { title: 'El Recluso', tone: 'mixed', text: 'Autonomía radical y aislamiento enfocado. Extraordinario para la maestría técnica de nicho, menos para la popularidad mundana.' },
    32: { title: 'La Combinación Mágica', tone: 'favorable', text: 'Poder de comunicación e influencia análogo al 5, 14 y 23. Favorable si mantienes tu propio criterio sin ceder ante la terquedad ajena.' },
    37: { title: 'La Alianza Próspera', tone: 'favorable', text: 'Amistades sinceras, sociedades armónicas y magnetismo. Compuesto extraordinario para la colaboración y la atracción.' },
    43: { title: 'Revolución', tone: 'caution', text: 'Transformaciones convulsas y lucha por el orden. Requiere canalizar la fuerza hacia la innovación constructiva y estructurada.' },
    51: { title: 'El Guerrero', tone: 'power', text: 'Naturaleza combativa y avance fulgurante en cualquier empresa. Despierta rivalidades; protege tu ascenso con estrategia.' },
  };

  const COMPOUND_ALIAS = { 33: 24, 34: 25, 35: 26, 36: 27, 38: 29, 39: 30, 40: 31, 41: 32, 42: 24, 44: 26, 45: 27, 46: 37, 47: 29, 48: 30, 49: 31, 50: 32, 52: 43 };

  function compoundHelper(n, lang) {
    if (n < 10 || n > 52) return null;
    const base = COMPOUND_BASE_EN[n] ? n : COMPOUND_ALIAS[n];
    if (!base) return null;
    const dict = lang === 'es' ? COMPOUND_BASE_ES : COMPOUND_BASE_EN;
    const c = dict[base];
    return Object.assign({ number: n, sharesWith: base !== n ? base : null }, c);
  }

  /* ===================================================================
     KABBALAH SEPHIROT & PILLARS
     =================================================================== */
  const SEPHIROT_TEXT_EN = {
    1: 'The point of origin. Numbers placed in Kether connect you to pure will and purpose before form: the seed of every decision you make.',
    2: 'Raw creative force and flashes of insight. Chokhmah holds your capacity for vision, bold initiation and the lightning strike of genius.',
    3: 'The great container. Binah gives form to force: structure, understanding, discernment and the wisdom of limits.',
    4: 'The throne of Jupiterian mercy. Chesed governs abundance, generosity, expansion and the ability to hold and grow resources.',
    5: 'The sword of Mars. Geburah governs discipline, boundaries, strength and the courage to cut away what does not serve.',
    6: 'The heart of the Tree. Tiferet harmonizes every other sphere: beauty, balance, magnetism and the integrated self.',
    7: 'The victory of Venus. Netzach governs desire, endurance, passion, art and the emotional fuel behind persistence.',
    8: 'The splendor of Mercury. Hod governs intellect, strategy, mathematics, language and systems of thought.',
    9: 'The foundation. Yesod is the blueprint layer where vision condenses into form just before it manifests in Malkuth, the material world.',
  };

  const SEPHIROT_TEXT_ES = {
    1: 'El punto de origen. Conecta con la voluntad pura y el propósito antes de la forma: la semilla de cada decisión soberana.',
    2: 'Fuerza creativa pura y destellos de intuición. Sostiene tu capacidad de visión y el rayo iniciador del genio.',
    3: 'El gran contenedor. Otorga estructura, discernimiento y la sabiduría de los límites que protegen la fuerza.',
    4: 'El trono de la misericordia jupiteriana. Rige la abundancia, la generosidad y la capacidad de expandir y sostener recursos.',
    5: 'La espada del rigor. Rige la disciplina, los límites firmes y la fortaleza para cortar lo que no sirve.',
    6: 'El corazón del Árbol. Armoniza todas las esferas: belleza, equilibrio, magnetismo y el ser integrado.',
    7: 'La victoria venusina. Rige el deseo, la resistencia, la pasión y el combustible emocional tras la persistencia.',
    8: 'El esplendor mercurial. Rige el intelecto, la estrategia, las matemáticas y los sistemas de pensamiento.',
    9: 'El fundamento. La capa de diseño donde la visión se condensa antes de manifestarse en Malkuth, el mundo material.',
  };

  const PILLAR_TEXT_EN = {
    Mercy: 'Your Tree leans toward the Pillar of Mercy: expansive, intuitive, generous and growth-oriented. You build by saying yes. Your work is restraint: adding Geburah-style boundaries so your abundance does not leak.',
    Severity: 'Your Tree leans toward the Pillar of Severity: disciplined, analytical, boundaried and strategic. You build by cutting. Your work is receptivity: letting Chesed-style generosity and alliance multiply what you have structured.',
    Mildness: 'Your Tree leans toward the Middle Pillar of Mildness: centered, integrating and harmonizing. You are the bridge between force and form. Your work is choosing a side decisively when the moment demands polarity.',
    Balanced: 'Your Tree is balanced across multiple pillars. You can access expansion, discipline and equilibrium as needed. Your work is knowing which pillar the current season requires and committing fully to it.',
  };

  const PILLAR_TEXT_ES = {
    Mercy: 'Tu Árbol se inclina hacia la Columna de la Misericordia: expansivo, intuitivo y orientado al crecimiento. Construyes diciendo sí. Tu trabajo es la contención: límites tipo Geburah para que tu abundancia no se filtre.',
    Severity: 'Tu Árbol se inclina hacia la Columna del Rigor: disciplinado, analítico y estratégico. Construyes cortando lo superfluo. Tu trabajo es la receptividad: alianzas tipo Chesed para multiplicar lo estructurado.',
    Mildness: 'Tu Árbol se inclina hacia la Columna Central del Equilibrio: centrado, integrador y armonizador. Eres el puente entre la fuerza y la forma. Tu trabajo es la polaridad decidida cuando el momento lo exige.',
    Balanced: 'Tu Árbol se encuentra equilibrado a través de múltiples columnas. Accedes a expansión, disciplina y equilibrio según la temporada. Tu maestría radica en comprometerte con la columna que la estación demanda.',
  };

  /* ===================================================================
     VEDIC NAVAGRAHA
     =================================================================== */
  const VEDIC_TEXT_EN = {
    1: 'Surya grants sovereignty, visibility and command. You are meant to be seen and to lead from the centre.',
    2: 'Chandra grants intuition, emotional intelligence and public appeal. You lead through feeling and timing.',
    3: 'Guru grants wisdom, ethics, teaching and expansion. Resources gather around your counsel.',
    4: 'Rahu grants unconventional breakthroughs, technology and sudden rises through structures others overlook.',
    5: 'Budha grants commerce, intelligence, speech and adaptability. You profit from information and exchange.',
    6: 'Shukra grants luxury, beauty, magnetism and wealth through refinement, art and partnership.',
    7: 'Ketu grants penetrating insight, research and spiritual detachment. Your edge is seeing beneath surfaces.',
    8: 'Shani is the Yogakaraka wealth engine: authority, endurance and long-term power earned through discipline.',
    9: 'Mangala grants courage, execution and competitive fire. You win by acting decisively.',
  };

  const VEDIC_TEXT_ES = {
    1: 'Surya otorga soberanía, visibilidad y mando central. Naciste para liderar desde el centro del escenario.',
    2: 'Chandra otorga intuición profunda y atracción pública. Diriges mediante la empatía y la sincronía temporal.',
    3: 'Guru otorga sabiduría, ética, visión y expansión. Los recursos y la autoridad gravitan en torno a tu consejo.',
    4: 'Rahu otorga avances no convencionales, tecnología y rupturas a través de estructuras que otros ignoran.',
    5: 'Budha otorga comercio, agilidad mental, elocuencia y velocidad táctica. Prosperas con la información y el intercambio.',
    6: 'Shukra otorga lujo, elegancia, magnetismo y riqueza mediante el refinamiento, el diseño y las alianzas de alto nivel.',
    7: 'Ketu otorga análisis penetrante, perspicacia de datos y desapego místico. Tu ventaja es ver bajo las apariencias.',
    8: 'Shani es el motor Yogakaraka de riqueza: autoridad, resistencia y poder patrimonial forjado mediante la disciplina.',
    9: 'Mangala otorga coraje, ejecución implacable y fuego competitivo. Ganas decidiendo y actuando con audacia.',
  };

  /* ===================================================================
     FIVE ELEMENTS & LO SHU
     =================================================================== */
  const ELEMENT_TEXT_EN = {
    Water: { color: '#3B82F6', direction: 'North', text: 'Water governs flow, career and the movement of opportunity. A strong Water profile networks easily and finds currents others miss.', activate: 'Place a moving-water feature or deep-blue objects in the North of your workspace; prioritize career visibility and networking.' },
    Earth: { color: '#C2A35A', direction: 'Centre, Southwest & Northeast', text: 'Earth governs stability, grounded wealth and The Mountain. A strong Earth profile accumulates slowly and holds what it earns. The 8 within Earth is the supreme wealth number (Fa).', activate: 'Anchor your workspace with crystals, ceramics and earth tones in the Centre and Northeast; favor real assets and long-term holds.' },
    Wood:  { color: '#6B8E23', direction: 'East & Southeast', text: 'Wood governs growth, expansion and the Southeast Wealth Corner. A strong Wood profile grows businesses organically and compounds influence.', activate: 'Activate the Southeast corner of your home or office with healthy plants and green tones; invest in growth assets.' },
    Metal: { color: '#C0C0C8', direction: 'West & Northwest', text: 'Metal governs precision, leadership and The Impenetrable Vault. A strong Metal profile cuts cleanly, decides precisely and protects capital.', activate: 'Use metallic objects, white and gold tones in the West and Northwest; formalize your financial defenses and leadership structures.' },
    Fire:  { color: '#DC2626', direction: 'South', text: 'Fire governs fame, visibility and recognition. A strong Fire profile is meant to be seen and remembered.', activate: 'Brighten the South of your space with warm light and red accents; invest deliberately in reputation, PR and personal brand.' },
  };

  const ELEMENT_TEXT_ES = {
    Water: { color: '#3B82F6', direction: 'Norte', text: 'El Agua rige el flujo, la trayectoria profesional y la corriente de oportunidades. Un perfil con Agua fluye con agilidad y detecta corrientes que otros pasan por alto.', activate: 'Coloca un elemento de agua en movimiento o tonos azul marino en el Norte de tu espacio; prioriza la visibilidad profesional.' },
    Earth: { color: '#C2A35A', direction: 'Centro, Suroeste y Noreste', text: 'La Tierra rige la estabilidad, el patrimonio consolidado y la Montaña. Acumula con paciencia y protege lo ganado. El 8 en Tierra es la riqueza suprema (Fa, 發).', activate: 'Ancla tu espacio con cerámica, cuarzos y tonos tierra en el Centro y Noreste; invierte en activos tangibles y reservas de largo plazo.' },
    Wood:  { color: '#6B8E23', direction: 'Este y Sureste', text: 'La Madera rige el crecimiento orgánico, la expansión y la Esquina de la Riqueza Sureste. Escala negocios con solidez y multiplica tu influencia.', activate: 'Activa la esquina Sureste de tu oficina con plantas vivas y tonos verdes; invierte decididamente en activos de crecimiento.' },
    Metal: { color: '#C0C0C8', direction: 'Oeste y Noroeste', text: 'El Metal rige la precisión, el liderazgo y la Bóveda Impenetrable. Corta con nitidez, decide con exactitud y protege el capital.', activate: 'Incorpora detalles metálicos, blanco y oro en el Oeste y Noroeste; formaliza tus blindajes patrimoniales y defensas operativas.' },
    Fire:  { color: '#DC2626', direction: 'Sur', text: 'El Fuego rige la fama, la reputación y el reconocimiento público. Naciste para ser visto, respetado y recordado con distinción.', activate: 'Ilumina el Sur de tu espacio con luz cálida y detalles en rojo; invierte deliberadamente en reputación y posicionamiento personal.' },
  };

  const ARROW_TEXT_EN = {
    mental:        { strong: 'Sharp memory, analytical power and strategic intelligence.', weak: 'Tendency to act before thinking; build deliberate planning rituals.' },
    emotional:     { strong: 'Emotional balance, spiritual sensitivity and depth of feeling.', weak: 'Emotions can feel muted or guarded; practice expression and connection.' },
    practical:     { strong: 'Material competence: you make things real and handle money practically.', weak: 'Ideas may outpace execution; pair vision with practical operators.' },
    thought:       { strong: 'A natural planner with a gift for organized, sequential thinking.', weak: 'Plans may lack structure; use written systems and checklists.' },
    will:          { strong: 'Powerful determination and the will to see goals through.', weak: 'Motivation can fluctuate; tie goals to deeper purpose.' },
    action:        { strong: 'Strong drive to execute and turn plans into motion.', weak: 'Hesitation before action; set deadlines and public commitments.' },
    determination: { strong: 'Persistence: you keep going long after others quit.', weak: 'You may abandon things early; commit to finishing cycles.' },
    prosperity:    { strong: 'The Golden Arrow: a natural capacity to attract and hold material prosperity.', weak: 'Wealth must be built consciously; formal budgeting and asset-building close the gap.' },
  };

  const ARROW_TEXT_ES = {
    mental:        { strong: 'Memoria aguda, capacidad analítica e inteligencia estratégica sobresaliente.', weak: 'Tendencia a actuar antes de planificar; establece rituales deliberados de diseño estratégico.' },
    emotional:     { strong: 'Equilibrio emocional, sensibilidad espiritual y profundidad de convicción.', weak: 'Las emociones pueden sentirse reservadas; cultiva la comunicación auténtica y el vínculo empático.' },
    practical:     { strong: 'Solvencia material: capacidad probada para aterrizar visiones y administrar recursos.', weak: 'Las ideas pueden rebasar la ejecución; alíate con operadores prácticos para cerrar la brecha.' },
    thought:       { strong: 'Planificador nato con don para el pensamiento secuencial y estructurado.', weak: 'Los planes pueden carecer de método; utiliza protocolos escritos y listas de control.' },
    will:          { strong: 'Voluntad inquebrantable y determinación férrea para culminar objetivos.', weak: 'La motivación puede oscilar; vincula cada meta a una causa superior trascendente.' },
    action:        { strong: 'Fuerte impulso hacia la ejecución y el movimiento táctico oportuno.', weak: 'Riesgo de vacilación previa a la acción; fija plazos inflexibles y compromisos públicos.' },
    determination: { strong: 'Persistencia ejemplar: sigues adelante mucho después de que otros desisten.', weak: 'Peligro de abandonar proyectos antes de tiempo; comprométete a cerrar ciclos completos.' },
    prosperity:    { strong: 'La Flecha de Oro: capacidad innata para atraer y consolidar prosperidad material.', weak: 'La riqueza debe forjarse metódicamente; presupuestos formales y acumulación de activos cierran la brecha.' },
  };

  /* ===================================================================
     ROSICRUCIAN 52-DAY CYCLES
     =================================================================== */
  const CYCLE_TEXT_EN = [
    { mode: 'PRESS EDGES', modeTone: 'press', directive: 'The Solar Period opens your personal year. Visibility is amplified: this is the time to seek promotion, ask for the raise, approach people in authority and step into leadership roles.', do: ['Request meetings with decision-makers and investors', 'Launch or relaunch your personal brand', 'Apply for promotions, titles and public positions'], avoid: ['Hiding in the background', 'Starting legal disputes with authority figures'] },
    { mode: 'CALIBRATE', modeTone: 'calibrate', directive: 'The Lunar Period is fluid and changeable. Ideal for short trips, quick pivots, testing ideas and tuning into public sentiment. Do not lock in long-term commitments.', do: ['Travel, scout and gather intelligence', 'Run small tests and quick experiments', 'Refine your offer based on feedback'], avoid: ['Signing long-term contracts', 'Major speculative financial bets'] },
    { mode: 'PRESS EDGES', modeTone: 'press', directive: 'The Martial Period favors bold, aggressive action and competition. Energy is high and variance is high: press your advantages, but guard against conflict and impulsive risk.', do: ['Make bold competitive moves', 'Push through stalled projects with force', 'Negotiate hard from a position of strength'], avoid: ['Unnecessary confrontation', 'Over-leveraging on impulse'] },
    { mode: 'BUILD', modeTone: 'build', directive: 'The Mercurial Period sharpens the intellect. Ideal for analysis, writing, systems-building, learning and negotiating contracts. Build the machine that will scale in the next period.', do: ['Write, research and design systems', 'Audit finances and optimize processes', 'Sign well-researched agreements'], avoid: ['Gossip and careless speech', 'Rushed decisions without data'] },
    { mode: 'MAXIMUM EXPANSION', modeTone: 'press', directive: 'The Jupiterian Period is your annual wealth window. Expansion, prosperity and high-stakes execution are favored. This is the time to scale, invest, ask for big money and make your largest moves.', do: ['Scale what is already working', 'Make major investments and acquisitions', 'Pitch your biggest deals and raise capital'], avoid: ['Playing small or hoarding', 'Wasting the window on low-leverage tasks'] },
    { mode: 'MAGNETIZE', modeTone: 'calibrate', directive: 'The Venusian Period amplifies social magnetism, attraction and partnership. Ideal for networking, romance, luxury, design and forming alliances. Money flows through relationships.', do: ['Host events and expand your network', 'Form strategic partnerships', 'Invest in aesthetics, branding and presentation'], avoid: ['Isolation', 'Overindulgence and emotional spending'] },
    { mode: 'PRESERVE CAPITAL', modeTone: 'preserve', directive: 'The Saturnian Period closes your personal year. Tighten ranges, prune what is not working and defend the vault. Not the time for new speculation; it is the time for discipline, review and patient preparation.', do: ['Cut losing positions and dead projects', 'Pay down debt and build reserves', 'Plan next year\'s Solar launch in detail'], avoid: ['New speculative ventures', 'Major expansions or large purchases'] },
  ];

  const CYCLE_TEXT_ES = [
    { mode: 'AVANZAR / EXPANDIR', modeTone: 'press', directive: 'El Período Solar inaugura tu año personal. La visibilidad se amplifica: es el momento de buscar ascensos, acercarte a figuras de autoridad y asumir posiciones de liderazgo.', do: ['Solicitar reuniones con tomadores de decisiones e inversionistas', 'Lanzar o renovar tu marca personal y ofertas clave', 'Postular a cargos, títulos y roles de alta visibilidad'], avoid: ['Ocultarte en segundo plano', 'Iniciar disputas legales con figuras de autoridad'] },
    { mode: 'CALIBRAR', modeTone: 'calibrate', directive: 'El Período Lunar es fluido y cambiante. Ideal para viajes cortos, giros rápidos, probar hipótesis y sintonizar con la opinión pública.', do: ['Viajar, explorar y levantar inteligencia de mercado', 'Lanzar micro-experimentos de validación rápida', 'Refinar tu propuesta en base al feedback de clientes'], avoid: ['Firmar compromisos rígidos de largo plazo', 'Grandes apuestas financieras especulativas'] },
    { mode: 'EJECUTAR', modeTone: 'press', directive: 'El Período Marcial favorece la acción audaz, agresiva y competitiva. La energía y la varianza son altas: presiona tus ventajas con rigor.', do: ['Realizar movimientos competitivos audaces', 'Destrabar proyectos estancados con fuerza resolutiva', 'Negociar con firmeza desde una postura de fortaleza'], avoid: ['Confrontaciones innecesarias por orgullo', 'Sobreapalancamiento por impulso emocional'] },
    { mode: 'CONSTRUIR', modeTone: 'build', directive: 'El Período Mercurial agudiza el intelecto. Ideal para análisis, redacción de acuerdos, construcción de sistemas y auditoría estratégica.', do: ['Redactar, investigar y diseñar sistemas operativos', 'Auditar finanzas y optimizar procesos de negocio', 'Firmar acuerdos exhaustivamente estructurados'], avoid: ['Comunicaciones imprudentes o rumores', 'Decisiones apresuradas sin respaldo de datos'] },
    { mode: 'MÁXIMA EXPANSIÓN', modeTone: 'press', directive: 'El Período Jupiteriano es tu ventana anual de riqueza suprema. La expansión, la prosperidad y la ejecución de alto riesgo están favorecidas.', do: ['Escalar lo que ya funciona y genera tracción', 'Realizar inversiones mayores y adquisiciones de activos', 'Presentar tus mayores propuestas comerciales y levantar capital'], avoid: ['Jugar a pequeña escala o postergar por temor', 'Desperdiciar la ventana en tareas operativas menores'] },
    { mode: 'MAGNETIZAR', modeTone: 'calibrate', directive: 'El Período Venusino amplifica el magnetismo social, la atracción y las alianzas. Ideal para networking de alto nivel, diseño y colaboraciones.', do: ['Organizar eventos y expandir tu red de contactos clave', 'Forjar alianzas comerciales y asociaciones estratégicas', 'Invertir en estética, diseño de marca y presentación personal'], avoid: ['Aislamiento social', 'Gastos desmedidos impulsados por la emoción'] },
    { mode: 'PRESERVAR CAPITAL', modeTone: 'preserve', directive: 'El Período Saturniano cierra tu año personal. Ajusta rangos, poda lo que no rinde y defiende la bóveda. Tiempo de revisión, consolidación y reserva.', do: ['Liquidar posiciones perdedoras y proyectos sin retorno', 'Amortizar deudas y fortalecer reservas de liquidez', 'Planificar detalladamente el lanzamiento Solar del próximo año'], avoid: ['Nuevas aventuras especulativas', 'Expansiones agresivas o compras mayores impulsivas'] },
  ];

  /* ===================================================================
     PERSONAL YEAR
     =================================================================== */
  const PERSONAL_YEAR_EN = {
    1: 'New beginnings. Plant seeds, launch and initiate.',
    2: 'Patience and partnership. Cultivate alliances; let seeds root.',
    3: 'Expression and expansion. Publish, speak and socialize.',
    4: 'Foundation-building. Systems, discipline and hard work pay off.',
    5: 'Change and freedom. Pivot, travel and embrace the unexpected.',
    6: 'Responsibility and harmony. Home, family and premium service.',
    7: 'Reflection and mastery. Study, refine and go deep.',
    8: 'Harvest and power. Money, authority and material results.',
    9: 'Completion. Release, finish cycles and prepare for renewal.',
  };

  const PERSONAL_YEAR_ES = {
    1: 'Nuevos comienzos. Siembra semillas, lanza proyectos e inicia con audacia.',
    2: 'Paciencia y alianzas. Cultiva relaciones clave; permite que las raíces maduren.',
    3: 'Expresión y expansión. Comunica, publica y amplía tu círculo de influencia.',
    4: 'Cimientos y estructura. Los sistemas, la disciplina y el trabajo riguroso rinden fruto.',
    5: 'Transformación y libertad. Reorienta rumbos, viaja y abraza lo imprevisto.',
    6: 'Responsabilidad y armonía. Hogar, familia y entrega de servicios de alta gama.',
    7: 'Reflexión y maestría. Estudia, audita, refina y profundiza en tu nicho.',
    8: 'Cosecha y poder patrimonial. Resultados materiales, autoridad y expansión de capital.',
    9: 'Culminación. Cierra ciclos, despréndete de lo obsoleto y prepara el renacer.',
  };

  const SYSTEM_INFO_EN = [
    { key: 'Pythagorean', name: 'Pythagorean', origin: 'Ancient Greece · 6th c. BCE', blurb: 'The Western mathematical system: letters mapped 1–9 in sequence to reveal your path, expression and inner drives.' },
    { key: 'Chaldean', name: 'Chaldean', origin: 'Babylon · Mesopotamia', blurb: 'The oldest sound-vibration system. Letters carry 1–8 by frequency; 9 is sacred. Compound numbers hold the hidden story.' },
    { key: 'Kabbalistic', name: 'Kabbalistic', origin: 'Hebrew Mysticism', blurb: 'Your core numbers placed on the Tree of Life and its ten Sephirot, revealing your pillar balance between force and form.' },
    { key: 'Vedic', name: 'Vedic / Tamil', origin: 'Ancient India', blurb: 'Driver, Conductor and Name numbers ruled by the Navagraha, the nine planetary intelligences of Jyotish.' },
    { key: 'Lo Shu', name: 'Chinese Lo Shu', origin: 'Ancient China · Yellow River', blurb: 'The 3×3 magic square and the Five Elements, mapping your birth digits into planes of strength and wealth.' },
  ];

  const SYSTEM_INFO_ES = [
    { key: 'Pythagorean', name: 'Pitagórico', origin: 'Antigua Grecia · Siglo VI a. C.', blurb: 'El sistema matemático occidental: letras del 1 al 9 para revelar tu sendero de vida, expresión y motivaciones íntimas.' },
    { key: 'Chaldean', name: 'Caldeo', origin: 'Babilonia · Mesopotamia', blurb: 'El sistema de vibración acústica más antiguo. Letras del 1 al 8 por frecuencia; el 9 es sagrado. Los compuestos revelan la historia profunda.' },
    { key: 'Kabbalistic', name: 'Cabalístico', origin: 'Misticismo Hebreo', blurb: 'Tus números esenciales sobre el Árbol de la Vida y sus diez Sephirot, revelando el equilibrio entre fuerza y forma.' },
    { key: 'Vedic', name: 'Védico / Tamil', origin: 'India Antigua', blurb: 'Números Psíquico (Driver), Destino (Conductor) y Nombre gobernados por los Navagraha, las nueve inteligencias planetarias.' },
    { key: 'Lo Shu', name: 'Lo Shu Chino', origin: 'China Antigua · Río Amarillo', blurb: 'El cuadrado mágico 3×3 y los Cinco Elementos, mapeando tus cifras de nacimiento en planos de fortaleza y riqueza material.' },
  ];

  /* ===================================================================
     UI LOCALIZATION DICTIONARIES
     =================================================================== */
  const UI_EN = {
    badge_systems: '5 Ancient Systems · 1 Code',
    hero_badge: 'Free 5-System Teaser Scan',
    hero_title: 'Why Western Numerology Only Gives You <span class="text-gold-grad">20%</span> of the Code.',
    hero_sub: 'Enter your name and birth date to run your profile through all <strong class="text-champagne font-semibold">5 Ancient Mathematical Systems</strong> (Pythagorean, Babylonian Chaldean, Kabbalistic, Vedic &amp; Chinese Lo Shu) to discover your <strong class="text-champagne font-semibold">Master Overlap Numbers</strong>.',
    form_label_name: 'Full Birth Name',
    form_placeholder_name: 'First and last name',
    form_label_dob: 'Date of Birth',
    form_label_email: 'Email Address',
    form_placeholder_email: 'Where should we send your results?',
    form_submit: 'Calculate My 5-System Overlap',
    form_submit_sub: '(Free Teaser)',
    founder_sample: '✦ Load Founder Sample (Adam Vega)',
    privacy_notice: 'Private. Never shared.',
    unlock_notice: '✦ Purchase confirmed. Enter (or confirm) your details below to generate your full Sovereign Dossier.',
    strip_eyebrow: 'The 5 Systems We Cross-Reference',
    scan_complete: '✓ 5-System Scan Complete',
    decoded_title: '${first}, your code has been decoded.',
    decoded_sub: 'We ran <span class="text-champagne">${fullName}</span> · ${birthLabel} through 5 ancient systems and ${totalSources} core calculations. Below is the 20% we can reveal for free.',
    anchor_1_eyebrow: 'Your #1 Master Signature Anchor',
    appeared_text: 'Appeared <b>${count}×</b> in your core numbers, overlapping across <b>${systemsCount} of 5</b> systems:',
    matrix_eyebrow: 'Your 5-System Alignment Matrix',
    matrix_title: 'You\'re looking at <span class="text-gold-grad">20%</span> of your code.',
    unlocked_badge: 'Unlocked',
    locked_badge: 'Locked',
    problem_eyebrow: 'Why one system isn\'t enough',
    problem_title: 'Reading one system is like hearing one instrument and calling it the symphony.',
    problem_p1: 'Every free numerology app runs the <b class="text-champagne">Pythagorean</b> system and stops. But the Babylonians, the Kabbalists, the Vedic seers and the Chinese masters each encoded a different layer of the same mathematics.',
    problem_p2: 'When the <b class="text-champagne">same number surfaces independently across multiple ancient traditions</b>, it stops being a coincidence. That is your <b class="text-champagne">Master Overlap</b>: the signal hidden beneath the noise.',
    problem_p3: 'Your #1 anchor, <b class="text-gold">${anchorNum}</b>, is only the first of three. Your <b class="text-champagne">#2 Wealth Engine</b> reveals exactly how money is meant to move toward you, and your <b class="text-champagne">52-Day Cycle Calendar</b> shows when to press and when to protect the vault.',
    vsl_eyebrow: 'Founder Briefing',
    vsl_title: 'Watch: How the 5 Systems Decode You',
    inside_eyebrow: 'Inside Your Sovereign Dossier',
    inside_title: '15 sections. 5 systems. One unified code.',
    checkout_eyebrow: 'Instant Access · One-Time Payment',
    checkout_title: 'Unlock the Other 80%',
    checkout_product: 'The Complete 5-System Sovereign Blueprint Dossier',
    checkout_product_sub: 'Instant access + printable luxury PDF · Personalized for ${first}',
    bump_title: '➜ One-Time Offer · +${bumpPrice}',
    bump_text: '<b>YES!</b> Add My Personalized 365-Day Rosicrucian 52-Day Cycles Calendar so I know my exact <b class="text-champagne">High-Wealth Action Windows</b> vs. <b class="text-champagne">Capital Preservation Windows</b> for the entire year.',
    total_today: 'Total today',
    unlock_cta: 'Unlock My Full Dossier · ',
    secure_badge: '🔒 Secure<br/>Stripe',
    instant_badge: '⚡ Instant<br/>Access',
    guarantee_badge: '✦ 30-Day<br/>Guarantee',
    pdf_badge: '✦ Printable<br/>PDF',
    demo_btn: '⚙ Simulate Successful Purchase / Unlock Full Dossier Now (Demo Mode)',
    questions_eyebrow: 'Questions',
    run_different: '← Run a different name',
    unlocked_access: 'Unlocked · Full Access',
    print_tip: 'Tip: in the print dialog choose <em>Save as PDF</em> and enable <em>Background graphics</em>.',
    print_btn: '⤓ Download / Print Luxury PDF Dossier',
    restart_btn: 'New Profile',
    disclaimer_footer: '© ${year} Sovereign 5-System. For entertainment, self-reflection and educational purposes only. Not financial, medical, legal or psychological advice.',
    ritual_align: 'Aligning the systems…',
    ritual_cross: 'Cross-referencing 5 ancient traditions',
    cover_edition: 'Private & Confidential · Edition ${year}',
    cover_prepared: 'Prepared exclusively for',
    cover_born: 'Born ${birthLabel}',
    cover_big3: 'The Big Three Master Overlap Numbers',
    cover_issued: 'Issued ${generatedLabel} · Pythagorean · Chaldean · Kabbalistic · Vedic · Lo Shu',
    method_title: 'The 5-System Method',
    method_eyebrow: 'Orientation',
    method_lead: 'Each ancient tradition encoded a different layer of the same mathematics. Read alone, any one system is partial. Read together, the numbers that recur across them reveal your true signature.',
    contents_eyebrow: 'Contents',
    overlap_eyebrow: 'The Core Product of This Dossier',
    overlap_title: 'Your Big Three Master Overlap Anchors',
    overlap_lead: 'We extracted ${totalSources} primary outputs across all five systems and tallied every recurrence of the numbers 1–9. The numbers that surface again and again, independently, are your Master Overlap Anchors.',
    frequency_tally: 'Frequency Tally (1–9)',
    source_calcs: 'Source Calculations',
    secondary_harmonics: 'Secondary Harmonics',
    sec_harmonics_desc: 'Complementary harmonic currents supporting your primary blueprint',
    codex_title: 'The Sovereign Codex',
    codex_eyebrow: 'Closing',
    codex_lead: 'Your entire five-system code on a single page. Return to it before major decisions.',
    codex_disclaimer: 'This dossier is provided for entertainment, self-reflection and educational purposes. It draws on traditional numerological systems and is not financial, investment, medical, legal or psychological advice. All calculations are deterministic and reproducible from the name and birth date provided.',
    signature_role: 'Primary Signature Anchor',
    wealth_role: 'Secondary Wealth & Strategy Engine',
    foundation_role: 'Tertiary Structural Foundation',
    signature_sub: 'Who You Are — Core Identity',
    wealth_sub: 'How You Materialize Abundance',
    foundation_sub: 'Your Grounding & Boundary Mechanism',
    claim_title: 'Order Confirmed · 100% Unlocked',
    claim_desc: 'Enter your Name & Birth Date to generate your unlocked 15-page Sovereign Dossier:',
    claim_btn: '✦ Generate My Dossier & PDF',
  };

  const UI_ES = {
    badge_systems: '5 Sistemas Antiguos · 1 Código',
    hero_badge: 'Escaneo Teaser de 5 Sistemas (Gratuito)',
    hero_title: 'Por Qué la Numerología Occidental Solo Te Da el <span class="text-gold-grad">20%</span> del Código.',
    hero_sub: 'Ingresa tu nombre y fecha de nacimiento para procesar tu perfil a través de los <strong class="text-champagne font-semibold">5 Sistemas Matemáticos Antiguos</strong> (Pitagórico, Caldeo Babilónico, Cabalístico, Védico y Lo Shu Chino) y revelar tus <strong class="text-champagne font-semibold">Números de Coincidencia Maestra</strong>.',
    form_label_name: 'Nombre de Nacimiento Completo',
    form_placeholder_name: 'Primer nombre y apellidos',
    form_label_dob: 'Fecha de Nacimiento',
    form_label_email: 'Correo Electrónico',
    form_placeholder_email: '¿Dónde enviamos tus resultados?',
    form_submit: 'Calcular Mi Coincidencia de 5 Sistemas',
    form_submit_sub: '(Teaser Gratuito)',
    founder_sample: '✦ Cargar Muestra Fundador (Adam Vega)',
    privacy_notice: 'Privado. Jamás compartido.',
    unlock_notice: '✦ Compra confirmada. Ingresa (o confirma) tus datos para generar tu Dossier Soberano completo.',
    strip_eyebrow: 'Los 5 Sistemas Que Cruzamos',
    scan_complete: '✓ Escaneo de 5 Sistemas Completado',
    decoded_title: '${first}, tu código ha sido descifrado.',
    decoded_sub: 'Procesamos a <span class="text-champagne">${fullName}</span> · ${birthLabel} a través de 5 sistemas antiguos y ${totalSources} cálculos fundamentales. A continuación, el 20% que podemos revelar gratuitamente.',
    anchor_1_eyebrow: 'Tu Ancla de Firma Primaria #1',
    appeared_text: 'Apareció <b>${count}×</b> en tus números esenciales, coincidiendo en <b>${systemsCount} de 5</b> sistemas:',
    matrix_eyebrow: 'Tu Matriz de Alineación de 5 Sistemas',
    matrix_title: 'Estás viendo solo el <span class="text-gold-grad">20%</span> de tu código.',
    unlocked_badge: 'Desbloqueado',
    locked_badge: 'Bloqueado',
    problem_eyebrow: 'Por qué un solo sistema no es suficiente',
    problem_title: 'Leer un solo sistema es como escuchar un instrumento y llamarlo sinfonía.',
    problem_p1: 'Cada aplicación gratuita ejecuta el sistema <b class="text-champagne">Pitagórico</b> y se detiene. Pero los babilonios, cabalistas, sabios védicos y maestros chinos codificaron capas distintas de la misma matemática.',
    problem_p2: 'Cuando el <b class="text-champagne">mismo número surge de forma independiente en múltiples tradiciones antiguas</b>, deja de ser casualidad. Esa es tu <b class="text-champagne">Coincidencia Maestra</b>: la señal pura bajo el ruido.',
    problem_p3: 'Tu ancla #1, <b class="text-gold">${anchorNum}</b>, es solo la primera de tres. Tu <b class="text-champagne">#2 Motor de Riqueza</b> revela exactamente cómo debe fluir el capital hacia ti, y tu <b class="text-champagne">Calendario de Ciclos de 52 Días</b> marca cuándo acelerar y cuándo proteger la bóveda.',
    vsl_eyebrow: 'Sesión con el Fundador',
    vsl_title: 'Video: Cómo los 5 Sistemas Descifran Tu Código',
    inside_eyebrow: 'Dentro de Tu Dossier Soberano',
    inside_title: '15 secciones. 5 sistemas. Un código unificado.',
    checkout_eyebrow: 'Acceso Inmediato · Pago Único',
    checkout_title: 'Desbloquea el Otro 80%',
    checkout_product: 'El Dossier Soberano Completo de los 5 Sistemas',
    checkout_product_sub: 'Acceso inmediato + PDF de lujo para imprimir · Personalizado para ${first}',
    bump_title: '➜ Oferta Única · +${bumpPrice}',
    bump_text: '<b>¡SÍ!</b> Añadir Mi Calendario Rosacruz de Ciclos de 52 Días (365 días) para conocer mis <b class="text-champagne">Ventanas de Máxima Riqueza</b> vs. <b class="text-champagne">Ventanas de Preservación de Capital</b> para todo el año.',
    total_today: 'Total hoy',
    unlock_cta: 'Desbloquear Mi Dossier Completo · ',
    secure_badge: '🔒 Pago Seguro<br/>Stripe',
    instant_badge: '⚡ Acceso<br/>Inmediato',
    guarantee_badge: '✦ Garantía de<br/>30 Días',
    pdf_badge: '✦ PDF de Lujo<br/>Imprimible',
    demo_btn: '⚙ Simular Compra Exitosa / Desbloquear Dossier Ahora (Modo Demo)',
    questions_eyebrow: 'Preguntas Frecuentes',
    run_different: '← Consultar otro nombre',
    unlocked_access: 'Desbloqueado · Acceso Total',
    print_tip: 'Sugerencia: en el diálogo de impresión selecciona <em>Guardar como PDF</em> y activa <em>Gráficos de fondo</em>.',
    print_btn: '⤓ Descargar / Imprimir Dossier PDF de Lujo',
    restart_btn: 'Nuevo Perfil',
    disclaimer_footer: '© ${year} Sovereign 5-System. Con fines de entretenimiento, auto-reflexión y educación exclusivamente. No constituye asesoramiento financiero, médico, legal ni psicológico.',
    ritual_align: 'Alineando los 5 sistemas…',
    ritual_cross: 'Cruzando 5 tradiciones matemáticas milenarias',
    cover_edition: 'Privado y Confidencial · Edición ${year}',
    cover_prepared: 'Preparado exclusivamente para',
    cover_born: 'Fecha de nacimiento: ${birthLabel}',
    cover_big3: 'Los Tres Números de Coincidencia Maestra',
    cover_issued: 'Emitido el ${generatedLabel} · Pitagórico · Caldeo · Cabalístico · Védico · Lo Shu',
    method_title: 'El Método de los 5 Sistemas',
    method_eyebrow: 'Orientación',
    method_lead: 'Cada tradición antigua codificó una capa distinta de la misma matemática universal. Aislado, cualquier sistema es incompleto. Analizados en conjunto, los números que se repiten revelan tu verdadera firma.',
    contents_eyebrow: 'Contenido del Dossier',
    overlap_eyebrow: 'El Producto Central de Este Dossier',
    overlap_title: 'Tus Tres Anclas de Coincidencia Maestra',
    overlap_lead: 'Cruzamos ${totalSources} resultados fundamentales en los cinco sistemas y registramos cada recurrencia de los números 1 al 9. Los que surgen reiteradamente son tus Anclas de Coincidencia Maestra.',
    frequency_tally: 'Frecuencia de Ocurrencia (1–9)',
    source_calcs: 'Cálculos de Origen',
    secondary_harmonics: 'Armónicos Secundarios',
    sec_harmonics_desc: 'Corrientes armónicas complementarias que respaldan tu arquitectura esencial',
    codex_title: 'El Códice Soberano',
    codex_eyebrow: 'Cierre',
    codex_lead: 'Todo tu código de cinco sistemas condensado en una sola página. Consúltalo antes de cada decisión estratégica.',
    codex_disclaimer: 'Este dossier se proporciona con fines de entretenimiento, auto-reflexión y educación. Se basa en tradiciones numerológicas clásicas y no constituye asesoramiento financiero, de inversión, médico, legal ni psicológico. Todos los cálculos son deterministas y reproducibles a partir del nombre y la fecha de nacimiento proporcionados.',
    signature_role: 'Ancla de Firma Primaria',
    wealth_role: 'Motor Secundario de Riqueza y Estrategia',
    foundation_role: 'Fundación Estructural Terciaria',
    signature_sub: 'Quién Eres — Identidad Esencial',
    wealth_sub: 'Cómo Materializas la Abundancia',
    foundation_sub: 'Tu Mecanismo de Anclaje y Límites',
    claim_title: 'Orden Confirmada · 100% Desbloqueado',
    claim_desc: 'Ingresa tu Nombre y Fecha de Nacimiento para generar tu Dossier Soberano de 15 páginas:',
    claim_btn: '✦ Generar Mi Dossier y PDF',
  };

  /* ===================================================================
     UNIFIED RESOLVER
     =================================================================== */
  function getBundle(lang) {
    const isEs = lang === 'es';
    return {
      lang: isEs ? 'es' : 'en',
      ARCHETYPES: isEs ? ARCHETYPES_ES : ARCHETYPES_EN,
      compound: (n) => compoundHelper(n, isEs ? 'es' : 'en'),
      SEPHIROT_TEXT: isEs ? SEPHIROT_TEXT_ES : SEPHIROT_TEXT_EN,
      PILLAR_TEXT: isEs ? PILLAR_TEXT_ES : PILLAR_TEXT_EN,
      VEDIC_TEXT: isEs ? VEDIC_TEXT_ES : VEDIC_TEXT_EN,
      ELEMENT_TEXT: isEs ? ELEMENT_TEXT_ES : ELEMENT_TEXT_EN,
      ARROW_TEXT: isEs ? ARROW_TEXT_ES : ARROW_TEXT_EN,
      CYCLE_TEXT: isEs ? CYCLE_TEXT_ES : CYCLE_TEXT_EN,
      PERSONAL_YEAR: isEs ? PERSONAL_YEAR_ES : PERSONAL_YEAR_EN,
      SYSTEM_INFO: isEs ? SYSTEM_INFO_ES : SYSTEM_INFO_EN,
      UI: isEs ? UI_ES : UI_EN,
    };
  }

  // Export root object
  root.S5Content = {
    get: getBundle,
    // Direct legacy / default English access:
    ARCHETYPES: ARCHETYPES_EN,
    compound: (n) => compoundHelper(n, 'en'),
    SEPHIROT_TEXT: SEPHIROT_TEXT_EN,
    PILLAR_TEXT: PILLAR_TEXT_EN,
    VEDIC_TEXT: VEDIC_TEXT_EN,
    ELEMENT_TEXT: ELEMENT_TEXT_EN,
    ARROW_TEXT: ARROW_TEXT_EN,
    CYCLE_TEXT: CYCLE_TEXT_EN,
    PERSONAL_YEAR: PERSONAL_YEAR_EN,
    SYSTEM_INFO: SYSTEM_INFO_EN,
    UI: UI_EN,
    // Raw language tables:
    EN: getBundle('en'),
    ES: getBundle('es'),
  };
})(typeof self !== 'undefined' ? self : this);
