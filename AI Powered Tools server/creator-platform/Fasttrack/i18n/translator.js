// Simple translator
const Translator = {
    currentLang: 'en',
    strings: {},
    
    init: async function(lang = 'en') {
        this.currentLang = lang;
        await this.loadStrings(lang);
        this.translatePage();
    },
    
    loadStrings: async function(lang) {
        try {
            const response = await fetch(`i18n/${lang}.json`);
            this.strings[lang] = await response.json();
        } catch (error) {
            console.error('Failed to load translations:', error);
        }
    },
    
    translatePage: function() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (this.strings[this.currentLang] && this.strings[this.currentLang][key]) {
                element.textContent = this.strings[this.currentLang][key];
            }
        });
    },
    
    t: function(key) {
        return this.strings[this.currentLang]?.[key] || key;
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    Translator.init('en');
});

// Global function
window.setLanguage = (lang) => {
    Translator.init(lang);
};