console.log('[main.js] Cargando...');

const MuniGo = {
    AUTH_TOKEN_KEY: 'access_token',
    
    getToken: function() {
        return localStorage.getItem(this.AUTH_TOKEN_KEY);
    },
    
    setToken: function(token) {
        localStorage.setItem(this.AUTH_TOKEN_KEY, token);
    },
    
    removeToken: function() {
        localStorage.removeItem(this.AUTH_TOKEN_KEY);
    },
    
    isAuthenticated: function() {
        return !!this.getToken();
    }
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('[main.js] DOM listo');
    console.log('[main.js] Token en localStorage:', MuniGo.getToken() ? 'SI' : 'NO');
});

console.log('[main.js] Cargado completamente');
