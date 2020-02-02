var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var firebase = require("firebase/app");
const firebaseConfig = {
  apiKey: "AIzaSyAqtshzyxIgJ5H2u-6Npdr6RqTLcj59rhs",
  authDomain: "soteria-hacksc.firebaseapp.com",
  databaseURL: "https://soteria-hacksc.firebaseio.com",
  projectId: "soteria-hacksc",
  storageBucket: "soteria-hacksc.appspot.com",
  messagingSenderId: "165646889105",
  appId: "1:165646889105:web:5e3fcaac368324266d4f30",
  measurementId: "G-E579WNK313"
};

firebase.initializeApp(firebaseConfig);

// Get a reference to the database service

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');
var location = require('./routes/location');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'hbs');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);
app.use('/getLocationAlert', location)

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
